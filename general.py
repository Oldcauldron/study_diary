
import sqlite3
from datetime import datetime, timedelta
import sys
import re

CONNECT_TABLE = 'diary.sqlite'
TIMEFORM = '%Y-%m-%d %H:%M'
PERIODFORM = '%Y %B'


def format_user_answer_time(user_answer: str) -> str:
    '''
    Take user's time input, and if it's Null return current_time,
    else check answer, transform it and return in right format
    '%Y-%m-%d %H:%M'
    '''
    pattern = r'(\d{4})\D{0,}(\d{2})\D{0,}(\d{2})\D{0,}(\d{2})\D{0,}(\d{2})'
    if not user_answer:
        user_answer = datetime.now().strftime(TIMEFORM)
    match = re.search(pattern, user_answer)
    user_answer = f'{match[1]}-{match[2]}-{match[3]} {match[4]}:{match[5]}'
    return user_answer


def scrub(table_name):
    # change query to str, clear from garbage like '; --'
    return ''.join(chr for chr in table_name if chr.isalnum())


def standart_sql_query(qry: str, fetchall=True):
    con = sqlite3.connect(CONNECT_TABLE)
    try:
        if fetchall is True:
            result = con.cursor().execute(qry).fetchall()
            return result
        else:
            con.cursor().execute(qry)
            con.commit()
    except sqlite3.DatabaseError as Err:
        if fetchall is True:
            print('Error: ', Err)
            return None

    finally:
        con.close()


def extract_discipline_summary_time(discipline: str, period) -> tuple:
    '''
    Find total time for discipline for this month. Return =>
    (26, 15, 49, datetime.timedelta(days=1, seconds=8149))
    '''
    qry = f"""
    select dt.start_time, dt.finish_time, d.discipline
    from diary_table dt, disciplines d
    where dt.discipline = d.rowid and d.discipline = '{discipline}'
    """
    x = standart_sql_query(qry, fetchall=True)
    summary_time = timedelta()
    for row in x:
        # ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'django')
        st, ft, di = row
        start = datetime.strptime(st, TIMEFORM)
        if start.month == period:
            finish = datetime.strptime(ft, TIMEFORM)
            summary_time += (finish - start)
    seconds = summary_time.total_seconds()
    timetuple = (int(seconds // 3600), int((seconds % 3600) // 60),
                 int(seconds % 60), summary_time)
    return timetuple


def create_all_tables():
    '''
    test with test_existing_table(table:str)
    if some table not exist, create it
    '''

    query2 = f'''create table if not exists diary_table
                (start_time timestamp,
                 discipline int,
                 finish_time timestamp,
                 FOREIGN KEY(discipline) REFERENCES disciplines(rowid))'''
    query1 = f'''create table if not exists disciplines
                (discipline text)'''
    query3 = f'''create table if not exists SOME
                (test text,
                 name text)'''
    queries = [query1, query2, query3]

    for query in queries:
        con = sqlite3.connect(CONNECT_TABLE)
        try:
            con.cursor().execute(query)
        finally:
            con.close()
    return True


def add_new_discipline(discipline: str) -> bool:
    qry = f"""
        insert into disciplines
        (discipline)
        values
        ('{discipline}')
    """
    standart_sql_query(qry, fetchall=False)
    return True


def add_new_session(start, discipline: str, fin='None') -> bool:
    '''
    Insert into diary_table new session
    '''
    qry = f"""
        select rowid
        from disciplines
        where discipline = '{discipline}'
    """
    rowid = standart_sql_query(qry, fetchall=True)

    qry = f"""
        insert into diary_table
        (start_time, discipline, finish_time)
        values
        ('{start}', {rowid[0][0]}, '{fin}')
    """
    standart_sql_query(qry, fetchall=False)
    return True


def close_current_session(open_sessions, close_session) -> bool:
    '''
    Close current session by actual moment, or other time if user write time.
    Open session is [(17, 'postgres', '2020-02-18 16:57:52.240594')]
    '''
    # sessions in timeformat fot check
    cl_sess = datetime.strptime(close_session, TIMEFORM)
    op_sess = datetime.strptime(open_sessions[0][2], TIMEFORM)

    if cl_sess < op_sess:
        print(f'You input close session in - {close_session} '
              f'but your open session - {op_sess}, it mean that your '
              'finish before your start. Try again something better.')
        return False
    qry = f"""
            UPDATE diary_table
            set finish_time = '{close_session}'
            where finish_time = 'None' and rowid = {open_sessions[0][0]}
    """
    standart_sql_query(qry, fetchall=False)
    return True


def get_list_of_disciplines(with_time=False):
    '''
    create query to disciplines table, and return list_of_disciplines if
    with_time = False, or return disc_and_time_dict
    (show time interval for this month) If with_time=True
    '''
    period = datetime.now()
    query = 'select rowid, discipline from disciplines'
    list_of_disciplines = [i[1] for i in standart_sql_query(query)]
    disc_and_time_dict = {}
    if with_time is False:
        return list_of_disciplines
    else:
        for d in list_of_disciplines:
            disc_and_time_dict[d] = extract_discipline_summary_time(
                d, period.month)
        return disc_and_time_dict, period


def list_of_open_sessions() ->tuple:
    '''
    find open sessions if it is. Return =>
    [(17, 'postgres', '2020-02-18 16:57:52.240594')]
    '''
    qry = f"""
    select dt.rowid, d.discipline, dt.start_time
    from diary_table dt, disciplines d
    where dt.discipline = d.rowid and dt.finish_time = 'None'
    """
    x = standart_sql_query(qry, fetchall=True)
    return x


def perfect_func(ld: dict) ->list:
    '''
    transform to convenient form and sorting.
    return =>
    [
    ('netology', (28, 30, 0, datetime.timedelta(seconds=16200))),
    ('django  ', (23, 58, 0, datetime.timedelta(seconds=86280))),
    ('css     ', (23, 34, 0, datetime.timedelta(seconds=84840))),
    ]
    '''
    grant = len(max(ld))
    new_ld = {}
    for d in ld.keys():
        len_d = len(d)
        different = grant - len_d
        d2 = f'''{d} {different * ' '}'''
        new_ld[d2] = ld[d]
    list_ld = list(new_ld.items())
    list_ld.sort(key=lambda x: -x[1][0])
    return list_ld


if __name__ == "__main__":

    '''
    разобрать sys.argv , задать при -а (более 1 аргумента) обрабатывать
    starttime disc fintime
    '''

    create_all_tables()  # test and create all tables if it not exist

    # Check open sessions and close them
    # -----------------------------
    open_sessions = list_of_open_sessions()
    if open_sessions:
        print(f'You should close the session - "{open_sessions[0][1]}", '
              f'which started {open_sessions[0][2]}')

        while True:
            try:
                close_session = input('Input time for finish in form '
                                      f'{datetime.now().strftime(TIMEFORM)} '
                                      'or just enter, in this case it will add'
                                      ' current time: ')

                close_session = format_user_answer_time(close_session)
                res = close_current_session(open_sessions, close_session)
                if res:
                    break
            except ValueError as Err:
                print(f'{Err}: ')
    # -------------------------------

    # Select the discipline or create
    # -------------------------------
    ld, period = get_list_of_disciplines(with_time=True)
    ld = perfect_func(ld)
    print(f'''\n\nStatistic for {period.strftime(PERIODFORM)} month\n\n''')
    for v in ld:
        print(
            f'''{v[0]} : {v[1][0]} hours, {v[1][1]} min, {v[1][2]} sec.
            [or {v[1][3]}]\n''')

    list_of_disciplines = get_list_of_disciplines()

    choose_disc_or_create = input(
        f'\n\nChoose discipline {list_of_disciplines}, '
        'create new or just enter for exit: ')

    if not choose_disc_or_create or choose_disc_or_create == 'exit':
        sys.exit()
    elif choose_disc_or_create not in list_of_disciplines:
        add_new_discipline(choose_disc_or_create)
    # -------------------------------

    # Choose starttime and start session
    # -------------------------------
    choose_time = input('Start session! Choose start-time in format '
                        f'{datetime.now().strftime(TIMEFORM)} '
                        'or just enter for current time: ')

    if not choose_time:
        choose_time = datetime.now().strftime(TIMEFORM)
    choose_time = format_user_answer_time(choose_time)
    start_session = add_new_session(choose_time, choose_disc_or_create)

    print('\n\n-------session will started---------\n\n')
