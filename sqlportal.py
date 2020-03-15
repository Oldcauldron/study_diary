import sqlite3


class SqlPortal:
    '''
    This class serves perform sql queries
    '''

    def __init__(self):
        self.connect_table = 'diary.sqlite'

    def standart_sql_query(self, qry: str, fetchall=True):
        con = sqlite3.connect(self.connect_table)
        try:
            if fetchall is True:
                result = con.cursor().execute(qry).fetchall()
                return result
            else:
                con.cursor().execute(qry)
                con.commit()
        except sqlite3.DatabaseError as Err:
            # if fetchall is True:
            print('Error from standart_sql_query: ', Err)
            return None

        finally:
            con.close()

    def create_all_tables(self):
        '''
        if some table not exist, create it
        '''

        query2 = f'''create table if not exists diary_table
                    (start_time timestamp,
                     discipline int,
                     finish_time timestamp,
                     FOREIGN KEY(discipline) REFERENCES disciplines(rowid))'''

        query1 = f'''create table if not exists disciplines
                    (discipline text)'''

        queries = [query1, query2]

        for query in queries:
            self.standart_sql_query(query, fetchall=False)

    def get_list_of_disciplines(self):
        qry = 'select discipline from disciplines'
        result = self.standart_sql_query(qry, fetchall=True)
        result = [i[0] for i in result]
        return result

    def add_new_discipline(self, discipline: str) -> bool:
        qry = f"""
            insert into disciplines
            (discipline)
            values
            ('{discipline}')
        """
        self.standart_sql_query(qry, fetchall=False)
        return True

    def list_of_open_sessions(self) ->tuple:
        '''
        find open sessions if it is. Return =>
        [(17, 'postgres', '2020-02-18 16:57')]
        '''
        qry = f"""
        select dt.rowid, d.discipline, dt.start_time
        from diary_table dt, disciplines d
        where dt.discipline = d.rowid and dt.finish_time = 'None'
        """
        x = self.standart_sql_query(qry, fetchall=True)
        return x

    def add_new_session(self, start, discipline: str, fin='None') -> bool:
        '''
        Insert into diary_table new session
        '''
        qry = f"""
            select rowid
            from disciplines
            where discipline = '{discipline}'
        """
        rowid = self.standart_sql_query(qry, fetchall=True)

        qry = f"""
            insert into diary_table
            (start_time, discipline, finish_time)
            values
            ('{start}', {rowid[0][0]}, '{fin}')
        """
        self.standart_sql_query(qry, fetchall=False)
        return True

    def close_current_session(self, open_sessions, close_session) -> bool:
        '''
        Close current sessn by actual moment, or other time if user write time.
        Open session is [(17, 'postgres', '2020-02-18 16:57:52.240594')]
        '''
        # sessions in timeformat fot check
        qry = f"""
                UPDATE diary_table
                set finish_time = '{close_session}'
                where finish_time = 'None' and rowid = {open_sessions[0][0]}
        """
        self.standart_sql_query(qry, fetchall=False)
        return True

    def get_all_sessions_from_discipline(self, discipline: str, period):
        '''
        Get list with tuple by start time and finish time from one discipline.
        # ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'django')
        '''
        qry = f"""
        select dt.start_time, dt.finish_time, d.discipline
        from diary_table dt, disciplines d
        where dt.discipline = d.rowid and d.discipline = '{discipline}'
        """
        result = self.standart_sql_query(qry, fetchall=True)
        return result

    def disciplines_time(self):
        '''
        [('2020-02-20 13:06', '2020-02-21 01:46', 'django'),
        ('2020-02-20 13:06', '2020-02-20 17:09', 'postgres'),
        ('2020-02-20 13:06', '2020-02-20 18:41', 'git'),]
        '''
        qry = f"""
        select dt.start_time, dt.finish_time, d.discipline
        from diary_table dt, disciplines d
        where dt.discipline = d.rowid
        """
        result = self.standart_sql_query(qry, fetchall=True)
        return result













