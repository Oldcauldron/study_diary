
from datetime import datetime, timedelta
import re
from pprint import pprint


class Sessions:

    def __init__(self, timeform):
        self.timeform = timeform

    def closability(self, open_sessions, close_session) -> bool:
        '''
        Check for close session time later then open session time
        '''
        cl_sess = datetime.strptime(close_session, self.timeform)
        op_sess = datetime.strptime(open_sessions[0][2], self.timeform)

        if cl_sess < op_sess:
            return False
        return True

    # def extract_disciplines_summary_time(self, disciplines, period) -> dict:
    #     '''
    #     [('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'django'),
    #     ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'sql'),
    #     ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'git'),]
    #     =>
    #     {'git': (4, 4, 0, datetime.timedelta(seconds=14640)),
    #     'sql': (0, 31, 0, datetime.timedelta(seconds=1860))}
    #     '''
    #     disciplines_time = {}
    #     summary_time = timedelta()
    #     for row in disciplines:
    #         # ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'django')
    #         st, ft, di = row
    #         start = datetime.strptime(st, self.timeform)
    #         if start.month == period.month:
    #             finish = datetime.strptime(ft, self.timeform)
    #             summary_time = disciplines_time.setdefault(di, timedelta())
    #             summary_time += (finish - start)
    #             disciplines_time[di] = summary_time
    #     for k in disciplines_time:
    #         seconds = disciplines_time[k].total_seconds()
    #         timetuple = (int(seconds // 3600), int((seconds % 3600) // 60),
    #                      int(seconds % 60), disciplines_time[k])
    #         disciplines_time[k] = timetuple
    #     return disciplines_time

    def extract_disciplines_summary_all_time(self, disciplines):
        '''
        [('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'django'),
        ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'sql'),
        ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'git'),]
        => {
        (year, month): {
                'git': (4, 4, 0, datetime.timedelta(seconds=14640)),
                'sql': (0, 31, 0, datetime.timedelta(seconds=1860)),
                },
            }
        '''
        main_dict = {}
        summary_time = timedelta()

        for row in disciplines:
            # ('2020-02-18 00:27:10', '2020-02-18 01:54:23', 'django')
            st, ft, di = row
            start = datetime.strptime(st, self.timeform)
            finish = datetime.strptime(ft, self.timeform)
            x = (start.year, start.month)
            if not main_dict.setdefault(x, False):
                main_dict[x] = {}
            summary_time = main_dict[x].setdefault(di, timedelta())
            summary_time += (finish - start)
            main_dict[x][di] = summary_time

        for date in main_dict:
            # (2020, 3)
            for k in main_dict[date]:
                # 'git': datetime.timedelta(seconds=14640),
                seconds = main_dict[date][k].total_seconds()
                timetuple = (int(seconds // 3600), int((seconds % 3600) // 60),
                             int(seconds % 60), main_dict[date][k])
                main_dict[date][k] = timetuple
        return main_dict

    def perfect_func(self, ld: dict) ->list:
        '''
        transform to convenient form with spaces and sorting.
        return =>
        [
        ('netology', (28, 30, 0, datetime.timedelta(seconds=16200))),
        ('django  ', (23, 58, 0, datetime.timedelta(seconds=86280))),
        ('css     ', (23, 34, 0, datetime.timedelta(seconds=84840))),
        ]
        '''
        max_len = len(max(ld, key=len))
        new_ld = {}
        for discipline in ld.keys():
            len_discipline = len(discipline)
            different = max_len - len_discipline
            d2 = f'''{discipline} {different * ' '}'''
            new_ld[d2] = ld[discipline]
        list_ld = list(new_ld.items())
        list_ld.sort(key=lambda x: -x[1][0])
        return list_ld

    def format_user_answer_time(self, user_answer: str) -> str:
        '''
        Take user's time input, and if it's Null return current_time,
        else check answer, transform it and return in right format
        '%Y-%m-%d %H:%M'
        '''
        ptrn = r'(\d{4})\D{0,}(\d{2})\D{0,}(\d{2})\D{0,}(\d{1,2})\D{0,}(\d{2})'
        if not user_answer:
            user_answer = datetime.now().strftime(self.timeform)
        match = re.search(ptrn, user_answer)
        user_answer = f'{match[1]}-{match[2]}-{match[3]} {match[4]}:{match[5]}'
        return user_answer

