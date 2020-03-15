
import sys
from datetime import datetime

from sqlportal import SqlPortal
from sessions import Sessions


TIMEFORM = '%Y-%m-%d %H:%M'
PERIODFORM = '%Y %B'


def scrub(table_name):
    # change query to str, clear from garbage like '; --'
    return ''.join(chr for chr in table_name if chr.isalnum())


if __name__ == "__main__":

    sql_port = SqlPortal()
    sess = Sessions(TIMEFORM)

    sql_port.create_all_tables()
    active_session = sql_port.list_of_open_sessions()

    # Check open sessions and close them
    # -----------------------------
    if active_session:
        print(f'You should close the session - "{active_session[0][1]}", '
              f'which started {active_session[0][2]}')
        while True:
            try:
                close_session = input('Input time for finish in form '
                                      f'{datetime.now().strftime(TIMEFORM)} '
                                      'or just enter, in this case it will add'
                                      ' current time: ')
                close_session = sess.format_user_answer_time(close_session)

                if not sess.closability(active_session, close_session):
                    print(f'You input incorrect closetime, '
                          f'it earlier than starttime, try again ')
                    continue

                closing_session = sql_port.close_current_session(
                    active_session, close_session)
                break
            except ValueError as Err:
                print(f'{Err}: ')

    # -------------------------------

    # Select the discipline or create
    # -------------------------------..

    period = datetime.now()

    list_of_disc = sql_port.get_list_of_disciplines()
    # ['django', 'postgres', 'git', 'netology', 'css', 'html', 'sql']

    all_disciplines_with_time = sql_port.disciplines_time()
    '''
    [('2020-02-20 13:06', '2020-02-21 01:46', 'django'),
    ('2020-02-20 13:06', '2020-02-20 17:09', 'postgres'),
    ('2020-02-20 13:06', '2020-02-20 18:41', 'git'),]
    '''

    disc_dict_with_sumtime2 = sess.extract_disciplines_summary_all_time(
        all_disciplines_with_time)
    '''
    {(2020, 2):
        {'django': (24, 4, 0, datetime.timedelta(days=1, seconds=240)),
        'postgres': (8, 21, 0, datetime.timedelta(seconds=30060)),}
    }
    '''

    if disc_dict_with_sumtime2:
        for k, v in disc_dict_with_sumtime2.items():
            disc_dict_with_sumtime = sess.perfect_func(v)
            dd = datetime.strftime(datetime(year=k[0], month=k[1], day=1),
                                   PERIODFORM)
            print(f'''\n\nStatistic for {dd}\n\n''')
            for v in disc_dict_with_sumtime:
                print(
                    f'''{v[0]} : {v[1][0]} hours, {v[1][1]} min, {v[1][2]} sec.
                    [or {v[1][3]}]\n''')

    choose_disc_or_create = input(
        f'\n\nChoose discipline {list_of_disc}, '
        'create new or just enter for exit: ')

    if not choose_disc_or_create or choose_disc_or_create == 'exit':
        sys.exit()
    elif choose_disc_or_create not in list_of_disc:
        sql_port.add_new_discipline(choose_disc_or_create)
    # -------------------------------

    # Choose starttime and start session
    # -------------------------------
    choose_time = input('Start session! Choose start-time in format '
                        f'{datetime.now().strftime(TIMEFORM)} '
                        'or just enter for current time: ')

    if not choose_time:
        choose_time = datetime.now().strftime(TIMEFORM)

    choose_time = sess.format_user_answer_time(choose_time)
    start_sess = sql_port.add_new_session(choose_time, choose_disc_or_create)

    print('\n\n-------session will started---------\n\n')
