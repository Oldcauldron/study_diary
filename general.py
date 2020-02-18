
import sqlite3
from datetime import datetime, timedelta
import sys

CONNECT_TABLE = 'diary.sqlite'

def scrub(table_name):
    # change query to str, clear from garbage like '; --'
    return ''.join(chr for chr in table_name if chr.isalnum())

'''
def test_existing_table(table:str) -> bool:
    # If table exists get True , else False
    query = f"select * from {scrub(table)}"
    con = sqlite3.connect('diary.sqlite')
    try:
        result = con.cursor().execute(query).fetchone()
        if result is not False:
            return True
    except sqlite3.DatabaseError as err:
        # print("Error: ", err)
        return False
    finally:
        con.close()
        '''

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

def extract_discipline_summary_time(discipline:str) -> tuple:
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
    hours, minutes = 0, 0
    for row in x:
        # ('2020-02-18 00:27:10.774271', '2020-02-18 01:54:23.774271', 'django')
        st, ft, di = row
        start = datetime.strptime(st, '%Y-%m-%d %H:%M:%S')
        if start.month == datetime.now().month:
            # finish = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S.%f')
            finish = datetime.strptime(ft, '%Y-%m-%d %H:%M:%S')
            summary_time += (finish - start)
    seconds = summary_time.total_seconds()
    timetuple = (int(seconds // 3600), int((seconds % 3600)//60),
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


def add_new_discipline(discipline:str) -> bool:
    qry = f"""
        insert into disciplines
        (discipline)
        values
        ('{discipline}')
    """
    standart_sql_query(qry, fetchall=False)
    return True
    

def add_new_session(start, discipline:str, fin='None') -> bool:
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
    Close current session by actual moment, or other time if user write time
    ''' 
    if len(close_session) == 0:
        # close_session = datetime.now()
        close_session = datetime.now().strftime('%Y-%m-%d %H:%M')
    else:
        close_session = datetime.strptime(close_session, '%Y-%m-%d %H:%M')
        op_sess = datetime.strptime(open_sessions[0][2], '%Y-%m-%d %H:%M:%S')
        if close_session < op_sess:
            print(f'You input close session in - {close_session} '
                f'but your open session - {op_sess}, it mean that your '
                'finish before your start. Try again something better.')
            sys.exit()
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
    with_time = False, or return dict_with_disc_and_time 
    (show time interval for this month) If with_time=True 
    '''
    query = 'select rowid, discipline from disciplines'
    list_of_disciplines = [i[1] for i in standart_sql_query(query)]
    dict_with_disc_and_time = {}
    if with_time is False:
        return list_of_disciplines
    else:
        for d in list_of_disciplines:
            dict_with_disc_and_time[d] = extract_discipline_summary_time(d)
        return dict_with_disc_and_time


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


def perfect_func(ld):
    grant = len(max(ld))
    new_ld = {}
    for d in ld.keys():
        len_d = len(d)
        different = grant - len_d
        d2 = f'''{d}{different * ' '}'''
        new_ld[d2] = ld[d]
    list_ld = list(new_ld.items())
    b = list_ld.sort(key=lambda x: -x[1][0])
    return list_ld


if __name__ == "__main__":

    create_all_tables()  # test and create all tables if it not exist

    open_sessions = list_of_open_sessions()
    if len(open_sessions) > 0:
        print(f'You should close the session - "{open_sessions[0][1]}", '
              f'which started {open_sessions[0][2]}')

        close_session = input('Input time for finish in form 2020-02-17 20:51 '
                       'or just enter, in this case it will add current time: ')
        close_current_session(open_sessions, close_session)

    ld = get_list_of_disciplines(with_time=True)
    ld = perfect_func(ld)
    for v in ld:
        print(f'{v[0]} : {v[1][0]} hours, {v[1][1]} min, {v[1][2]} sec. [or {v[1][3]}]\n')

    list_of_disciplines = get_list_of_disciplines()
    choose_discipline_or_create = input(
        f'\n\nChoose discipline {list_of_disciplines}, '
         'create new or just enter for exit: ')
    if not choose_discipline_or_create or choose_discipline_or_create == 'exit':
        sys.exit()
    elif choose_discipline_or_create not in list_of_disciplines:
        add_new_discipline(choose_discipline_or_create)

    choose_time = input('Start session! Choose start-time in format '
                        '2020-02-17 20:51 '
                        'or just enter for current time: ')

    if not choose_time:
        # choose_time = datetime.now()
        choose_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    else:
        choose_time = datetime.strptime(choose_time, '%Y-%m-%d %H:%M')

    start_session = add_new_session(choose_time, choose_discipline_or_create)

    print('session will started')































