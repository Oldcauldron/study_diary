
import sqlite3
from datetime import datetime

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
                (start_time timestamp,
                 discipline int,
                 finish_time timestamp)'''
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
    '''
    insert into disciplines
                    (discipline)
                    values
                    (%(discipline)s)
                    """, {'discipline': discipline})
    '''
    

def add_new_session(start:date=datetime.now(),
    discipline:str, fin:date=False) -> bool:
    '''
    Insert into diary_table new session
    '''
    pass

def close_current_session(fin:date=datetime.now()) -> bool:
    '''
    Close current session by actual moment, or other time if user write time
    ''' 
    pass


def get_list_of_disciplines(with_time=False) -> dict:
    '''
    create query to disciplines table, and return list 
    If with_time=True show time_interval for this month

    [('Argh',), ('Bargh',), ('Cargh',)]
    '''
    if with_time=False:
        query = 'select rowid, name from SOME'
        result = standart_sql_query(query)

def list_of_open_sessions() ->list:
    '''
    find open sessions if it is
    '''

if __name__ = "__main__":

    create_all_tables()  # test and create all tables if it not exist

    print(get_list_of_disciplines(with_time=True))

    open_sessions = list_of_open_sessions()
    if open_sessions:
        print('You should close the session {open_sessions}')
        close_session = input('Input time for finish or enter, in this case \
it will add current time')
        close_current_session(close_session)


    list_of_disciplines = get_list_of_disciplines()
    choose_discipline_or_create = input(
        f'Choose discipline ({list_of_disciplines}) or create new: '
        )
    if choose_discipline_or_create not in list_of_disciplines:
        add_new_discipline(choose_discipline_or_create)

    choose_time = input(
        f'Start session! Choose start-time in format 2020-02-17 20:51 \
or just enter for current time: '
        )

    if not choose_time:
        choose_time = datetime.now()

    start_session = add_new_session(choose_time,
    discipline=choose_discipline_or_create, fin:date=False)

    print('session will started')



































