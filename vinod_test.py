import django
import os
from django.db import models, connection
os.environ['DJANGO_SETTINGS_MODULE'] = 'Gateway.settings'  # configure()
django.setup()
from tracker.models import *
from main.models import *
import xlrd
from collections import OrderedDict
from django.db.models.functions import Cast
import calendar
from datetime import datetime
from django.db.models import Sum



class AnalysisScenes():

    def get_perv_next_months(self,start_date='', end_date=''):
        st_dte1 = start_date
        en_dte1 = end_date
        st_dte = datetime.strptime(st_dte1, "%b-%y").strftime("%Y-%m-%d")
        en_dte = datetime.strptime(en_dte1, "%b-%y").strftime("%Y-%m-%d")

        if st_dte == en_dte:
            proj_dates = [datetime.strptime(st_dte, "%Y-%m-%d").strftime("%b-%y")]
        else:
            dates = [str(st_dte), str(en_dte)]
            start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
            proj_dates = list(OrderedDict(
                ((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys()) + [
                             en_dte1]

        current_month = datetime.now().strftime('%b-%y')
        try:
            current_month_index = proj_dates.index(current_month)
            prev_dte = proj_dates[:current_month_index]
            next_dte = proj_dates[current_month_index:]
        except:
            prev_dte = []
            next_dte = proj_dates

        data = {'proj_dates': proj_dates, 'prev_dte': prev_dte, 'next_dte': next_dte}
        return data

    def generic_func_to_generate_months_wise_data(self,**kwargs):
        final_res = {}
        for proj in kwargs['PROJECTS']:
            final_res[proj] = {}
            for prc in kwargs['PROCESS']:
                if prc in ['blocking','secondary']:
                    prc ='Animation'
                final_res[proj][prc] = {}
                for mn in kwargs['ALL_MONTHS']['proj_dates']:
                    final_res[proj][prc][mn] = kwargs['data'].get(proj,{}).get(prc,{}).get(mn,0)
        return final_res

    def get_output_for_month_gross_planned(self,**kwargs):
        '''
            output_for_month_gross_sec = plannedOutputSecs Updated By PM in PARTICULAR SCENES (planned sec)
            Database Table : ScenesPlannedSecAndPoints
            Columns: planned_sec
        '''

        obj = ScenesPlannedSecAndPoints.objects.select_related('fk_project').values('project__code','month__month','month__year','process').annotate(count = Sum('planned_sec')).filter(project__code__in = kwargs['PROJECTS'],process__in = kwargs['PROCESS'])
        output_for_month_planned = {}
        for i in obj:
            month_name = "{0}-{1}".format(kwargs['MONTHS_DICT'].get(str(i['month__month'])),str(i['month__year'])[2:])
            proj = i['project__code']
            prc = i['process']
            cnt = i['count']
            if prc in ['blocking','secondary']:
                prc = 'Animation'
            if proj in output_for_month_planned:
                if prc in output_for_month_planned[proj]:
                    if month_name in output_for_month_planned[proj][prc]:
                        output_for_month_planned[proj][prc][month_name]+=cnt
                    else:
                        output_for_month_planned[proj][prc][month_name] = cnt
                else:
                    output_for_month_planned[proj][prc] = {month_name:cnt}
            else:
                output_for_month_planned[proj] = {prc:{month_name:cnt}}

        kwargs['data'] = output_for_month_planned
        final_res = self.generic_func_to_generate_months_wise_data(**kwargs)
        return final_res

    def get_output_for_month_gross_actual(self,**kwargs):
        sp={}
        sp['fk_task__fk_project__code__in'] = kwargs['PROJECTS']
        sp['fk_task__process__name__in'] = kwargs['PROCESS']
        Obj = Productivity.objects.select_related("fk_task",'fk_task__fk_project','fk_task__process',"fk_task__fk_shot").filter(**sp)
        actual_gross_month_output ={}
        for i in Obj:
            proj = i.fk_task.fk_project.code
            month_name = i.created_at.strftime("%b-%y")
            proc = i.fk_task.process.name
            try:
                frames = i.fk_task.fk_shot.frames
            except:
                frames = 0
            fbs =i.fk_task.fk_project.fps
            try:
                secs =float(frames)/float(fbs)
            except:
                secs = 0.0
            date =month_name

            if proc in ['blocking', 'secondary']:
                proc ="Animation"

            if proj in actual_gross_month_output:
                if proc in actual_gross_month_output[proj]:
                    if date in actual_gross_month_output[proj][proc]:
                        actual_gross_month_output[proj][proc][date]+=secs
                    else:
                        actual_gross_month_output[proj][proc][date] = secs
                else:
                    actual_gross_month_output[proj][proc] = {date: secs}
            else:
                actual_gross_month_output[proj] ={proc:{date:secs}}
        kwargs['data'] = actual_gross_month_output
        final_res = self.generic_func_to_generate_months_wise_data(**kwargs)
        return final_res

    def get_output_for_the_month_gross(self,**kwargs):
        actual = self.get_output_for_month_gross_actual(**kwargs)
        planned = self.get_output_for_month_gross_planned(**kwargs)
        return {'actual':actual,'planned':planned}

    def get_output_for_month_planned(self,planned = {}):
        '''
            outpuput for the month calculation same for both completed and coming months
            output_for_the_month = output_for_month_gross_sec/60
            output_for_month_gross_sec = plannedOutputSecs Updated By PM in PARTICULAR SCENES (planned sec)
            Database Table : ScenesPlannedSecAndPoints
            Columns: planned_sec

        '''
        output_for_month_planned = {}
        for proj,prc_data in planned.items():
            output_for_month_planned[proj] = {}
            for prc,mnth_data in prc_data.items():
                output_for_month_planned[proj][prc] = {}
                for mnth,val in mnth_data.items():
                    output_for_month_planned[proj][prc][mnth] = val/60
        return output_for_month_planned

    def get_output_for_month_actual(self,actual = {}):
        '''
            outpuput for the month calculation same for both completed and coming months
            output_for_the_month = output_for_month_gross_sec/60
            output_for_month_gross_sec = plannedOutputSecs Updated By PM in PARTICULAR SCENES (planned sec)
            Database Table : ScenesPlannedSecAndPoints
            Columns: planned_sec

        '''

        output_for_month_actual = {}
        for proj, prc_data in actual.items():
            output_for_month_actual[proj] = {}
            for prc, mnth_data in prc_data.items():
                output_for_month_actual[proj][prc] = {}
                for mnth, val in mnth_data.items():
                    output_for_month_actual[proj][prc][mnth] = val / 60
        return output_for_month_actual

    def get_output_for_the_month(self,output_for_the_month_gross = {}):
        actual = self.get_output_for_month_actual(actual=output_for_the_month_gross['actual'])
        planned = self.get_output_for_month_planned(planned = output_for_the_month_gross['planned'])
        return {'actual':actual,'planned':planned}

    def get_generic_upto_month_function(self,act_or_planned = {},col_name='',**kwargs):
        actual_data = {}
        planned_data = {}
        for proj in kwargs['PROJECTS']:
            actual_data[proj] = {}
            planned_data[proj] = {}
            current_month = datetime.now().strftime('%b-%y')
            try:
                current_month_index = kwargs['ALL_MONTHS']['proj_dates'].index(current_month)
                completed = kwargs['ALL_MONTHS']['proj_dates'][:current_month_index]
                #completed.append(current_month)
                coming = kwargs['ALL_MONTHS']['proj_dates'][current_month_index:]
            except:
                completed = []
                coming = proj_dates

            for prc in kwargs['PROCESS']:
                if prc in ['blocking','secondary']:
                    prc = 'Animation'
                act_incr_val = 0
                pln_incr_val = 0
                actual_data[proj][prc] = {}
                planned_data[proj][prc] = {}
                for mn in completed:
                    actual_val = kwargs['ACTUAL'].get(proj,{}).get(prc,{}).get(mn,0)
                    actual_data[proj][prc][mn] = act_incr_val+actual_val
                    act_incr_val += actual_val
                for mn in coming:
                    planned_val = kwargs['PLANNED'].get(proj, {}).get(prc, {}).get(mn, 0)
                    planned_data[proj][prc][mn] = act_incr_val + planned_val
                    act_incr_val += planned_val
        data = {'actual':actual_data,'planned':planned_data}
        return data

    def get_output_upto_month(self,**kwargs):
        params = {'PROJECTS':kwargs['PROJECTS'],'PROCESS':kwargs['PROCESS'],'ALL_MONTHS':kwargs['ALL_MONTHS'],
                  'ACTUAL':kwargs['OUTPUT_FOR_MONTH_GROSS']['actual'],'PLANNED':kwargs['OUTPUT_FOR_MONTH_GROSS']['planned'],
                  'COL_NAME':'output_for_month'}
        upto_month = self.get_generic_upto_month_function(**params)
        return {'actual':upto_month['actual'],'planned':upto_month['planned']}

    def output_upto_month_final(self,output_for_month_gross = {}):
        actual = self.get_generic_upto_month_function(output_for_month_gross['actual'])
        planned = self.get_generic_upto_month_function(output_for_month_gross['actual'])
        return {'actual':actual,'planned':planned}

    def get_output_for_the_month_take_1_80_percent_actual(self,actual={}):
        '''
            output_for_the_month_take_1_80_percent_actual = output_for_month_gross_sec*0.8
        '''
        data = {}
        for proj,prc_data in actual.items():
            data[proj] = {}
            for prc,mnth_data in prc_data.items():
                data[proj][prc] = {}
                for mnth,val in mnth_data.items():
                    data[proj][prc][mnth] = val*0.8
        return data

    def get_output_for_the_month_take_1_80_percent_planned(self,planned={}):
        '''
            output_for_the_month_take_1_80_percent_planned = output_for_month_gross_sec*0.8
        '''
        data = {}
        for proj,prc_data in planned.items():
            data[proj] = {}
            for prc,mnth_data in prc_data.items():
                data[proj][prc] = {}
                for mnth,val in mnth_data.items():
                    data[proj][prc][mnth] = val*0.8
        return data

    def get_output_for_the_month_take_1_80_percent(self,output_for_month_gross={}):
        actual = self.get_output_for_the_month_take_1_80_percent_actual(actual=output_for_month_gross['actual'])
        planned = self.get_output_for_the_month_take_1_80_percent_planned(planned = output_for_month_gross['planned'])
        return {'actual':actual,'planned':planned}

    def get_output_for_the_month_final_20_percent_actual(self,actual={}):
        '''
            output_for_the_month_take_1_80_percent_planned = output_for_month_gross_sec*0.2
        '''
        data = {}
        for proj,prc_data in actual.items():
            data[proj] = {}
            for prc,mnth_data in prc_data.items():
                data[proj][prc] = {}
                for mnth,val in mnth_data.items():
                    data[proj][prc][mnth] = val*0.2
        return data

    def get_output_for_the_month_final_20_percent_planned(self,planned = {}):
        '''
            output_for_the_month_take_1_80_percent_planned = output_for_month_gross_sec*0.2
        '''
        data = {}
        for proj,prc_data in planned.items():
            data[proj] = {}
            for prc,mnth_data in prc_data.items():
                data[proj][prc] = {}
                for mnth,val in mnth_data.items():
                    data[proj][prc][mnth] = val*0.2
        return data

    def get_output_for_the_month_final_20_percent(self,output_for_month_gross={}):
        actual = self.get_output_for_the_month_take_1_80_percent_actual(actual=output_for_month_gross['actual'])
        planned = self.get_output_for_the_month_take_1_80_percent_planned(planned = output_for_month_gross['planned'])
        return {'actual':actual,'planned':planned}

    def prod_available_capacity_points_planned(self,**kwargs):
        '''
            available_capacity_points_planned = output_for_month_gross_planned/manpower_for_month_planned
            ProductivityForAvailableCapacityPointsInSec = ((TargetBasedOnCTCInPoints_Previous / ManpowerForTheMonthInManMonth_Previous) * SecondsPerPointInRatio) /
                                                                                                      (1-PercentageFactor/100)
            percentage factors are taken from the incentive sheet from given cost analysis excels.


            planned_manpower = output_for_the_month_gross/available_capacity_points_planned

            planne_target = (current_month_manpower /prev_month_manpower) * prev_target_points

        '''

        percentage_factors = {'blocking':0.85,'secondary':0.85,'comp':0.85,'Animation':0.84,
                              'modeling':0,'texturing':0.85,'rigging':0.85,'lip_sync':0,'layout':0,'set_dressing':0,
                              'asset_hair':0,'lighting':0.85,'bg_matte_paint':0.85,'asset_comp':0.85,'facial':0.85,'fx':0.85,
                              'hair_simultaion':0}
        completed_months = kwargs['ALL_MONTHS']['prev_dte']
        coming_months = kwargs['ALL_MONTHS']['next_dte']
        #current_month = datetime.now().strftime('%b-%y')
        #coming_months.append(current_month)
        actual_mandays = kwargs['MANPOWER_FOR_THE_MONTH']['actual']
        actual_output_for_month_gross = kwargs['OUTPUT_FOR_MONTH_GROSS']
        actual_targets = kwargs['ACTUAL_TARGETS']['actual']
        planned_prod = kwargs['PLANNED_PROD']
        planned_capacity_target_manpower_obj = {}
        planned_capacity = {}
        for proj in kwargs['PROJECTS']:
            planned_capacity_target_manpower_obj[proj] = {}
            planned_capacity[proj] = {}
            for prc in kwargs['PROCESS']:
                if prc in ['blocking','secondary']:
                    prc ='Animation'
                planned_capacity_target_manpower_obj[proj][prc] = {}
                percnt_fctr = percentage_factors.get(prc, 0)
                planned_capacity[proj][prc] = {}
                for mn in kwargs['ALL_MONTHS']['proj_dates']:
                    current_month = datetime.strptime(mn,"%b-%y")
                    previous_month= current_month- timedelta(days=2)
                    current_mnth = current_month.strftime("%b-%y")
                    prev_mnth = previous_month.strftime("%b-%y")
                    planned_prod_val = planned_prod.get(proj, {}).get(prc, {}).get(mn, 0)

                    if prev_mnth in completed_months:
                        month_gross_val = actual_output_for_month_gross['actual'].get(proj, {}).get(prc, {}).get(mn, 0)
                        prev_month_target = actual_targets.get(proj,{}).get(prc,{}).get(prev_mnth,0)
                        current_month_manpower = actual_mandays.get(proj, {}).get(prc, {}).get(mn, 0)
                        prev_month_manpower = actual_mandays.get(proj,{}).get(prc,{}).get(prev_mnth,0)

                        #sec_points_val = sec_points['actual'].get(proj,{}).get(prc,{}).get(mn,{}).get('sec_per_point',0)

                        if mn == coming_months[0]:
                            try:
                                sec_points_val = planned_prod_val / 21.65
                            except:
                                sec_points_val = 0
                            month_gross_val = actual_output_for_month_gross['planned'].get(proj, {}).get(prc, {}).get(mn, 0)
                        else:
                            try:
                                sec_points_val = actual_output_for_month_gross.get(proj,{}).get(prc,{}).get(mn,0)/actual_targets.get(proj,{}).get(prc,{}).get(mn,0)
                            except:
                                sec_points_val =0
                        try:
                            val1 = (prev_month_target/prev_month_manpower)
                            val2 = val1*sec_points_val
                            val3 = val2/percnt_fctr
                            planned_capacity_points = val3
                        except:
                            planned_capacity_points = 0

                        try:
                            if mn == coming_months[0]:
                                curr_manpower = month_gross_val/planned_capacity_points
                            else:
                                curr_manpower = current_month_manpower
                            planned_target = (curr_manpower/prev_month_manpower)*prev_month_target
                        except:
                            planned_target = 0.0

                    elif prev_mnth in coming_months:
                        month_gross_val = actual_output_for_month_gross['planned'].get(proj, {}).get(prc, {}).get(mn, 0)
                        prev_month_target = planned_capacity_target_manpower_obj.get(proj,{}).get(prc,{}).get(prev_mnth,{}).get('planned_target',0)
                        current_month_manpower = planned_capacity_target_manpower_obj.get(proj, {}).get(prc, {}).get(mn, {}).get('planned_manpower',0)
                        prev_month_manpower = planned_capacity_target_manpower_obj.get(proj, {}).get(prc, {}).get(mn, {}).get('planned_manpower',0)
                        try:
                            sec_points_val = planned_prod_val/21.65
                        except:
                            sec_points_val = 0
                        try:
                            val1 = (prev_month_target / prev_month_manpower)
                            val2 = val* sec_points_val
                            val3 = val2/percnt_fctr
                            planned_capacity_points = val3
                        except:
                            planned_capacity_points = 0
                        try:
                            planned_target = (current_month_manpower / prev_month_manpower) * prev_month_target
                        except:
                            planned_target = 0.0
                    else:
                        planned_capacity_points = 0
                        planned_target = 0
                        prev_month_target = 0
                        prev_month_manpower = 0
                        sec_points_val = 0
                        planned_prod_val = 0
                        month_gross_val = 0

                    try:
                        planned_manpower = month_gross_val/planned_capacity_points
                    except:
                        planned_manpower = 0.0

                    # print ('month',mn)
                    # print ('previous mn',prev_mnth)
                    # print ('prev_month_target',prev_month_target)
                    # print ('prev_month_manpower',prev_month_manpower)
                    # print ('sec_points',sec_points_val)
                    # print ('planned_prod',planned_prod_val)
                    # print ('planned_capacity_points',planned_capacity_points)
                    # print ('planned_manpower',planned_manpower)
                    # print ('planned_target',planned_target)
                    # print ('output_for_the_month_gross',month_gross_val)
                    # print ("******"*10)

                    planned_capacity_target_manpower_obj[proj][prc][mn] = {'planned_capacity':planned_capacity_points,
                                                                           'planned_manpower':planned_manpower,
                                                                           'planned_target':planned_target}
                    planned_capacity[proj][prc][mn] = planned_capacity_points

        return {'all_data':planned_capacity_target_manpower_obj,'planned_capacity':planned_capacity}

    def prod_available_capacity_points_actual(self,**kwargs):
        '''
            prod_available_capacity_points_actual = output_for_the_month_actual/manpower_for_the_month_actual
        '''
        final_res = {}
        for proj in kwargs['PROJECTS']:
            final_res[proj] = {}
            for prc in kwargs['PROCESS']:
                if prc in ['blocking','secondary']:
                    prc ='Animation'
                final_res[proj][prc] = {}
                for mn in kwargs['ALL_MONTHS']['proj_dates']:
                    try:
                        output_for_month_gross = kwargs['OUTPUT_FOR_MONTH_GROSS'].get(proj,{}).get(prc,{}).get(mn,0)
                        manpower_for_month = kwargs['MANPOWER_FOR_THE_MONTH'].get(proj,{}).get(prc,{}).get(mn,0)
                        final_res[proj][prc][mn] = output_for_month_gross/manpower_for_month
                    except:
                        final_res[proj][prc][mn] = 0
        return final_res

    def get_prod_available_capacity_points(self,**kwargs):
        actual = self.prod_available_capacity_points_actual(**kwargs)
        planned_data = self.prod_available_capacity_points_planned(**kwargs)
        planned = planned_data['all_data']
        planned_capacity = planned_data['planned_capacity']
        return {'actual':actual,'planned':planned,'planned_capacity':planned_capacity}

    def get_manpower_for_month_actual(self,**kwargs):
        sp = {}
        sp['project__in'] = kwargs['PROJECTS']
        sp['process__in'] = kwargs['PROCESS']
        Obj = GatewayDailyAttandance.objects.filter(**sp)
        data = {}
        month_dict = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul',
                      '8': 'Aug', '9': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
        for i in Obj:
            proj = i.project
            date = i.created_at.strftime("%b-%y")
            proc = i.process
            try:
                val = (1 / 21.65)
            except:
                val = 0

            if proc in ['blocking', 'secondary']:
                proc = "Animation"

            if proj in data:
                if proc in data[proj]:
                    if date in data[proj][proc]:
                        data[proj][proc][date] += val
                    else:
                        data[proj][proc][date] = val
                else:
                    data[proj][proc] = {date: val}
            else:
                data[proj] = {proc: {date: val}}
        kwargs['data'] = data
        final_res = self.generic_func_to_generate_months_wise_data(**kwargs)
        return final_res

    def get_manpower_for_month_planned(self,**kwargs):
        data = {}
        kwargs['data'] = data
        final_res = self.generic_func_to_generate_months_wise_data(**kwargs)
        return final_res

    def get_manpower_for_month(self,**kwargs):
        actual = self.get_manpower_for_month_actual(**kwargs)
        #planned = self.get_manpower_for_month_planned(**kwargs)
        planned = {}
        return {'actual':actual,'planned':planned}

    def get_manpower_upto_month(self,**kwargs):
        params = {'PROJECTS':kwargs['PROJECTS'],'PROCESS':kwargs['PROCESS'],'ALL_MONTHS':kwargs['ALL_MONTHS'],
                  'ACTUAL':kwargs['MANPOWER_FOR_THE_MONTH']['actual'],'PLANNED':kwargs['OUTPUT_FOR_MONTH_GROSS']['planned'],
                  'COL_NAME':'output_for_month'}
        upto_month = self.get_generic_upto_month_function(**params)
        return {'actual':upto_month['actual'],'planned':upto_month['planned']}

    def get_targets_planned(self,**kwargs):
        data = {}
        return data

    def get_targets_actual(self,**kwargs):
        '''ACTUAL TARGET CALCUALTION'''
        sp = {}
        sp['process__in'] = kwargs['PROCESS']
        sp['project__in'] = kwargs['PROJECTS']
        DWDA = GatewayDailyAttandance.objects.select_related('fk_user').filter(**sp)
        gw_data = {}
        dd = []
        for i in DWDA:
            project = i.project
            month = i.created_at.month
            year = i.created_at.year
            user = i.fk_user.employee_id
            process =i.process
            # print(process)
            date = "{0}-{1}".format(month, year)
            dd.append(date)
            if project in gw_data:
                if process in gw_data[project]:
                    if date in gw_data[project][process]:
                        if user not in gw_data[project][process][date]:
                            gw_data[project][process][date].append(user)
                    else:
                        gw_data[project][process].update({date:[user]})
                else:
                    gw_data[project].update({process:{date: [user]}})
            else:
                gw_data[project] = {process:{date: [user]}}
        month_dict = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul',
                      '8': 'Aug', '9': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
        actual_capacity = {}
        for proj, v in gw_data.items():
            for proc, val in v.items():
                if proc in ['blocking','secondary']:
                    proc = 'Animation'
                for m, u in val.items():
                    sp = {}
                    sp["fk_user__employee_id__in"] = u
                    sp["created_at__month"] = m.split("-")[0]
                    sp["created_at__year"] = m.split("-")[1]
                    month = "{0}-{1}".format(month_dict.get(m.split("-")[0]), m.split("-")[1][2:])
                    for i in MonthlyTarget.objects.filter(**sp):
                        try:
                            trgt = float(i.actual_month_target)
                        except:
                            trgt = 0.0

                        if proj in actual_capacity:
                            if proc in actual_capacity[proj]:
                                if month in actual_capacity[proj][proc]:
                                    actual_capacity[proj][proc][month] += trgt
                                else:
                                    actual_capacity[proj][proc][month] = trgt
                            else:
                                actual_capacity[proj][proc] = {month: trgt}
                        else:
                            actual_capacity[proj] = {proc: {month: trgt}}


        kwargs['data'] = actual_capacity
        final_res = self.generic_func_to_generate_months_wise_data(**kwargs)
        return final_res
    def get_targets(self,**kwargs):
        planned = {}
        actual = self.get_targets_actual(**kwargs)
        return {'actual':actual,'planned':planned}

    def get_prod_for_month_planned(self,**kwargs):
        obj = ScenesPlannedSecAndPoints.objects.select_related('fk_project').values('project__code','month__month','month__year','process').annotate(count = Sum('planned_prod')).filter(project__code__in = kwargs['PROJECTS'],process__in = kwargs['PROCESS'])
        planned_prod = {}
        for i in obj:
            month_name = "{0}-{1}".format(kwargs['MONTHS_DICT'].get(str(i['month__month'])),str(i['month__year'])[2:])
            proj = i['project__code']
            prc = i['process']
            if prc in ['blocking','secondary']:
                prc = 'Animation'
            cnt = i['count']
            if proj in planned_prod:
                if prc in planned_prod[proj]:
                    if month_name in planned_prod[proj][prc]:
                        planned_prod[proj][prc][month_name]+=cnt
                    else:
                        planned_prod[proj][prc][month_name] =cnt
                else:
                    planned_prod[proj][prc] = {month_name:cnt}
            else:
                planned_prod[proj] = {prc:{month_name:cnt}}
        return planned_prod

    def get_prod_for_months_actual(self,**kwargs):
        '''
            productivity = (output_for_month_gross/capapcity)*21.65
            actual_sec_per_point = (output_for_month_gross/capapcity)
            episode_factor = 720
            ** episode_factor is a constant value  is from alc analysis 3rd row
            episode_per_point = episode_factor/capacity
        '''
        data = {}
        actual_output_for_month_gross = kwargs['OUTPUT_FOR_MONTH_GROSS']
        actual_targets = kwargs['ACTUAL_TARGETS']
        epside_factor = 720
        for proj in kwargs['PROJECTS']:
            data[proj] = {}
            for prc in kwargs['PROCESS']:
                if prc in ['blocking','secondary']:
                    prc ='Animation'
                data[proj][prc] = {}
                for mn in kwargs['ALL_MONTHS']['proj_dates']:
                    gross = actual_output_for_month_gross.get(proj,{}).get(prc,{}).get(mn,0)
                    target = actual_targets.get(proj,{}).get(prc,{}).get(mn,0)
                    try:
                        prod =(gross/target)*21.65
                        sec_per_point = (gross/target)
                    except:
                        prod = 0
                        sec_per_point = 0

                    try:
                        ep_per_point = epside_factor / target
                    except:
                        ep_per_point = 0

                    data[proj][prc][mn] = {'sec_per_point':0,'prod':prod,'ep_per_point':ep_per_point}
        return data

    def get_prod_for_month(self,**kwargs):
        planned = self.get_prod_for_month_planned(**kwargs)
        actual = self.get_prod_for_months_actual(**kwargs)
        return {'actual':actual,'planned':planned}

    def capacity_upto_month(self,**kwargs):
        params = {'PROJECTS': kwargs['PROJECTS'], 'PROCESS': kwargs['PROCESS'], 'ALL_MONTHS': kwargs['ALL_MONTHS'],
                  'ACTUAL': kwargs['ACTUAL_TARGETS']['actual'],
                  'PLANNED': kwargs['PLANNED_CAPACITY'],
                  'COL_NAME': 'output_for_month'}
        upto_month = self.get_generic_upto_month_function(**params)
        return {'actual': upto_month['actual'], 'planned': upto_month['planned']}

    def get_generic_analysis_stats_for_all_reports(self,**kwargs):
        '''
            available_capacity_points_planned = output_for_month_gross_planned/manpower_for_month_planned
            ProductivityForAvailableCapacityPointsInSec = ((TargetBasedOnCTCInPoints_Previous / ManpowerForTheMonthInManMonth_Previous) * SecondsPerPointInRatio) /
                                                                                                      (1-PercentageFactor/100)
            percentage factors are taken from the incentive sheet from given cost analysis excels.
            planned_manpower = output_for_the_month_gross/available_capacity_points_planned
            planne_target = (current_month_manpower /prev_month_manpower) * prev_target_points

        '''

        project = kwargs['PROJECT']
        process = kwargs['PROCESS']
        if process == 'Animation':
            process = ['blocking','secondary']
        else:
            process = [process]
        start = kwargs['START']
        end = kwargs['END']
        month_dict = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul',
                      '8': 'Aug', '9': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
        month_names = self.get_perv_next_months(start_date=start,end_date=end)
        all_months = month_names['proj_dates']
        compleated_months = month_names['prev_dte']
        coming_months = month_names['next_dte']
        params = {'PROJECTS':project,'PROCESS':process,'START':start,'END':end,'MONTHS_DICT':month_dict,'ALL_MONTHS':month_names}
        output_for_the_month_gross = self.get_output_for_the_month_gross(**params)
        params['OUTPUT_FOR_MONTH_GROSS'] = output_for_the_month_gross
        output_upto_month = self.get_output_upto_month(**params)
        manpower_for_the_month = self.get_manpower_for_month(**params)
        params['MANPOWER_FOR_THE_MONTH'] = manpower_for_the_month
        targets = self.get_targets(**params)
        manpower_upto_month = self.get_manpower_upto_month(**params)
        params['ACTUAL_TARGETS'] = targets
        prod_for_month_planned = self.get_prod_for_month_planned(**params)
        params['PLANNED_PROD'] = prod_for_month_planned
        prod_available_capacity_points = self.get_prod_available_capacity_points(**params)
        params['PLANNED_CAPACITY'] = prod_available_capacity_points['planned_capacity']
        capacity_upto_month = self.capacity_upto_month(**params)
        print (capacity_upto_month)
        #
        # for k,v in prod_available_capacity_points['planned'].items():
        #     pass
        #print (prod_available_capacity_points['planned'])
        #output_for_the_month = self.get_output_for_the_month(output_for_the_month_gross = output_for_the_month_gross)
        # #output_upto_month = self.get_output_upto_month(output_for_the_month = output_for_the_month)
        # output_for_month_take_one_80_percent = self.get_output_for_the_month_take_1_80_percent(output_for_month_gross=output_for_the_month_gross)
        # output_for_month_final_80_percent = self.get_output_for_the_month_final_20_percent(output_for_month_gross=output_for_the_month_gross)
        # output_upto_month_final = self.output_upto_month_final(output_for_month_gross=output_for_the_month_gross)
        # manpower_for_the_month = self.get_manpower_for_month(**params)
        # #manpower_upto_the_month = self.get_manpower_upto_month(manpower_for_the_month=manpower_for_the_month)
        # params['MANPOWER_FOR_THE_MONTH'] = manpower_for_the_month['actual']
        # targets = self.get_targets(**params)
        # params['ACTUAL_TARGETS'] = targets
        # productivity = self.get_prod_for_month(**params)
        # sec_points = productivity
        # params['SEC_POINTS'] = sec_points
        # prod_available_capacity_points = self.get_prod_available_capacity_points(**params)
        analysis_report = {}
        analysis_report['output_for_the_month_gross'] = output_for_the_month_gross
        analysis_report['coming'] = coming_months
        analysis_report['completed'] = compleated_months
        analysis_report['output_upto_month'] = output_upto_month
        analysis_report['manpower_for_the_month'] = manpower_for_the_month
        analysis_report['manpower_upto_month'] = manpower_upto_month
        analysis_report['targets'] = targets
        #analysis_report['productivity'] = productivity
        analysis_report['prod_available_capacity_points'] = prod_available_capacity_points
        analysis_report['prod_for_month_planned'] = prod_for_month_planned
        return analysis_report

    def get_anlysis_report(self,request):
        analysis_stats = self.get_generic_analysis_stats_for_all_reports(**request)
        #print (analysis_stats['targets'])
        #output_for_month = analysis_stats['targets']['actual']['power-players-series']['Animation']
        ## for k,v in output_for_month.items():
        #     print (k,"==",v)

# ob = AnalysisScenes()
# params = {'PROJECT':['power-players-series'],'PROCESS':'Animation','START':'Feb-18','END':'Aug-20'}
# res = ob.get_anlysis_report(params)
# def rsum(L):
#     if type(L) != list:
#         return L
#     if L == []:
#         return 0
#     return rsum(L[0]) + rsum(L[1:])
#
#
# print (rsum([1,2,[3,4],[5,6]]))


#GatewayDailyAttandance.objects.filter(fk_user__employee_id = '')


project = ['power-players-series']
process = ['secondary','blocking']


def get_perv_next_months(start_date='', end_date=''):
    st_dte1 = start_date
    en_dte1 = end_date
    st_dte = datetime.strptime(st_dte1, "%b-%y").strftime("%Y-%m-%d")
    en_dte = datetime.strptime(en_dte1, "%b-%y").strftime("%Y-%m-%d")

    if st_dte == en_dte:
        proj_dates = [datetime.strptime(st_dte, "%Y-%m-%d").strftime("%b-%y")]
    else:
        dates = [str(st_dte), str(en_dte)]
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
        proj_dates = list(OrderedDict(
            ((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys()) + [
                         en_dte1]

    current_month = datetime.now().strftime('%b-%y')
    try:
        current_month_index = proj_dates.index(current_month)
        prev_dte = proj_dates[:current_month_index]
        next_dte = proj_dates[current_month_index:]
    except:
        prev_dte = []
        next_dte = proj_dates

    data = {'all_months': proj_dates, 'completed': prev_dte, 'upcoming': next_dte}
    return data

def get_actual_seconds(**kwargs):
    sp = {}
    sp['fk_task__fk_project__code__in'] = kwargs['PROJECTS']
    sp['fk_task__process__name__in'] = kwargs['PROCESS']
    Obj = Productivity.objects.select_related("fk_task", 'fk_task__fk_project', 'fk_task__process',
                                              "fk_task__fk_shot").filter(**sp)
    actual_sec = {}
    for i in Obj:
        proj = i.fk_task.fk_project.code
        month_name = i.created_at.strftime("%b-%y")
        proc = i.fk_task.process.name
        if proc in ['blocking','secondary']:
            proc = 'Animation'
        try:
            frames = i.fk_task.fk_shot.frames
        except:
            frames = 0
        fbs = i.fk_task.fk_project.fps
        try:
            secs = float(frames) / float(fbs)
        except:
            secs = 0.0
        date = month_name

        if proc in ['blocking', 'secondary']:
            proc = "Animation"

        if proj in actual_sec:
            if proc in actual_sec[proj]:
                if date in actual_sec[proj][proc]:
                    actual_sec[proj][proc][date] += secs
                else:
                    actual_sec[proj][proc][date] = secs
            else:
                actual_sec[proj][proc] = {date: secs}
        else:
            actual_sec[proj] = {proc: {date: secs}}
    return actual_sec

def get_planned_scenes(**kwargs):
    obj = ScenesPlannedSecAndPoints.objects.select_related('project').filter(project__code__in=kwargs['PROJECTS'], process__in=kwargs['PROCESS'])
    planned_sec = {}
    planned_prod = {}
    for i in obj:
        proj = i.project.code
        prc = i.process
        if prc in ['secondary','blocking']:
            prc = 'Animation'
        sec = i.planned_sec
        prod = i.planned_prod
        mnth = i.month.strftime("%b-%y")

        if proj in planned_sec:
            if prc in planned_sec[proj]:
                if mnth in planned_sec[proj][prc]:
                    planned_sec[proj][prc][mnth]+= sec
                    planned_prod[proj][prc][mnth]+= prod
                else:
                    planned_sec[proj][prc][mnth]= sec
                    planned_prod[proj][prc][mnth]= prod
            else:
                planned_sec[proj][prc] = {mnth:sec}
                planned_prod[proj][prc]={mnth:sec}
        else:
            planned_sec[proj] = {prc:{mnth:sec}}
            planned_prod[proj] = {prc:{mnth:sec}}
    return {'planned_sec':planned_sec,'planned_prod':planned_prod}

def get_act_manpower(**kwargs):
    sp = {}
    sp['project__in'] = kwargs['PROJECTS']
    sp['process__in'] = kwargs['PROCESS']
    Obj = GatewayDailyAttandance.objects.filter(**sp)
    data = {}
    month_dict = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul',
                  '8': 'Aug', '9': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
    for i in Obj:
        proj = i.project
        date = i.created_at.strftime("%b-%y")
        proc = i.process
        try:
            val = (1 / 21.65)
        except:
            val = 0

        if proc in ['blocking', 'secondary']:
            proc = "Animation"

        if proj in data:
            if proc in data[proj]:
                if date in data[proj][proc]:
                    data[proj][proc][date] += val
                else:
                    data[proj][proc][date] = val
            else:
                data[proj][proc] = {date: val}
        else:
            data[proj] = {proc: {date: val}}
    return data

def get_act_targets(**kwargs):
    '''ACTUAL TARGET CALCUALTION'''
    sp = {}
    sp['process__in'] = kwargs['PROCESS']
    sp['project__in'] = kwargs['PROJECTS']
    DWDA = GatewayDailyAttandance.objects.select_related('fk_user').filter(**sp)
    gw_data = {}
    dd = []
    for i in DWDA:
        project = i.project
        month = i.created_at.month
        year = i.created_at.year
        user = i.fk_user.employee_id
        process = i.process
        # print(process)
        date = "{0}-{1}".format(month, year)
        dd.append(date)
        if project in gw_data:
            if process in gw_data[project]:
                if date in gw_data[project][process]:
                    if user not in gw_data[project][process][date]:
                        gw_data[project][process][date].append(user)
                else:
                    gw_data[project][process].update({date: [user]})
            else:
                gw_data[project].update({process: {date: [user]}})
        else:
            gw_data[project] = {process: {date: [user]}}
    month_dict = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul',
                  '8': 'Aug', '9': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
    actual_capacity = {}
    for proj, v in gw_data.items():
        for proc, val in v.items():
            if proc in ['blocking', 'secondary']:
                proc = 'Animation'
            for m, u in val.items():
                sp = {}
                sp["fk_user__employee_id__in"] = u
                sp["created_at__month"] = m.split("-")[0]
                sp["created_at__year"] = m.split("-")[1]
                month = "{0}-{1}".format(month_dict.get(m.split("-")[0]), m.split("-")[1][2:])
                for i in MonthlyTarget.objects.filter(**sp):
                    try:
                        trgt = float(i.actual_month_target)
                    except:
                        trgt = 0.0

                    if proj in actual_capacity:
                        if proc in actual_capacity[proj]:
                            if month in actual_capacity[proj][proc]:
                                actual_capacity[proj][proc][month] += trgt
                            else:
                                actual_capacity[proj][proc][month] = trgt
                        else:
                            actual_capacity[proj][proc] = {month: trgt}
                    else:
                        actual_capacity[proj] = {proc: {month: trgt}}

    return actual_capacity

def get_all_month_data(**kwargs):
    monthsObj = get_perv_next_months(start_date=kwargs['START'],end_date=kwargs['END'])
    print (monthsObj)
    act_sec = get_actual_seconds(**kwargs)
    act_prod = {}
    pln_scene_data = get_planned_scenes(**kwargs)
    pln_sec = pln_scene_data['planned_sec']
    pln_prod = pln_scene_data['planned_prod']
    act_targets = get_act_targets(**kwargs)
    act_manpower = get_act_manpower(**kwargs)

    actual_output_gross = {}
    planned_output_gross = {}
    actual_prod = {}
    planned_prod = {}
    actual_manpower ={}
    actual_targets = {}
    planned_manpower = {}
    planned_target = {}
    actual_prod_available_cap_point = {}
    planned_prod_available_cap_point = {}

    for proj in kwargs['PROJECTS']:
        actual_output_gross[proj] = {}
        planned_output_gross[proj] = {}
        actual_prod[proj] = {}
        planned_prod[proj] = {}
        actual_manpower[proj] = {}
        actual_targets[proj] = {}
        actual_prod_available_cap_point[proj] = {}
        for prc in kwargs['PROCESS']:
            if prc in ['blocking','secondary']:
                prc = 'Animation'
            actual_output_gross[proj][prc] = {}
            planned_output_gross[proj][prc] = {}
            actual_prod[proj][prc] = {}
            planned_prod[proj][prc] = {}
            actual_manpower[proj][prc] = {}
            actual_targets[proj][prc] = {}
            actual_prod_available_cap_point[proj][prc] = {}

            for mnth in monthsObj['all_months']:
                actual_output_gross[proj][prc][mnth] = act_sec.get(proj,{}).get(prc,{}).get(mnth,0)
                planned_output_gross[proj][prc][mnth] = pln_sec.get(proj,{}).get(prc,{}).get(mnth,0)
                actual_prod[proj][prc][mnth] = act_prod.get(proj,{}).get(prc,{}).get(mnth,0)
                planned_prod[proj][prc][mnth] = pln_prod.get(proj,{}).get(prc,{}).get(mnth,0)
                actual_manpower[proj][mnth] = act_targets.get(proj,{}).get(prc,{}).get(mnth,0)
                actual_targets[proj][mnth] = act_manpower.get(proj,{}).get(prc,{}).get(mnth,0)
                try:
                    actual_prod_available_cap_point[proj][prc][mnth] = act_sec.get(proj,{}).get(prc,{}).get(mnth,0)/act_targets.get(proj,{}).get(prc,{}).get(mnth,0)
                except:
                    actual_prod_available_cap_point[proj][prc][mnth] =0.0

                #print (monthsObj)

    for proj in kwargs['PROJECTS']:
        planned_manpower[proj] = {}
        planned_target[proj] = {}
        planned_prod_available_cap_point[proj] = {}
        for prc in kwargs['PROCESS']:
            planned_manpower[proj][prc] = {}
            planned_target[proj][prc] = {}
            planned_prod_available_cap_point[proj][prc] = {}
            for mnth in monthsObj['all_months']:
                current_month = datetime.strptime(mn, "%b-%y")
                previous_month = current_month - timedelta(days=2)
                prev_mnth = previous_month.strftime("%b-%y")
                if prev_mnth in monthsObj['completed']:
                    prev_target =actual_targets.get(proj,{}).get(prc).get(prev_mnth,0)
                    prev_manpower =actual_manpower.get(proj,{}).get(prc).get(prev_mnth,0)
                else:
                    prev_target =planned_target_targets.get(proj,{}).get(prc).get(prev_mnth,0)
                    prev_manpower =planned_manpower.get.get(proj,{}).get(prc).get(prev_mnth,0)

                if mnth in monthsObj['complete']:
                    try:
                        sec_per_ratio = actual_output_gross.get(proj,{}).get(prc).get(prev_mnth,0)/actual_targets.get(proj,{}).get(prc).get(prev_mnth,0)
                    except:
                        sec_per_ratio = 0
                else:
                    try:
                        sec_per_ratio = planned_output_gross.get(proj,{}).get(prc).get(prev_mnth,0)/planned_target_targets.get(proj,{}).get(prc).get(prev_mnth,0)
                    except:
                        sec_per_ratio = 0




                planned_manpower[proj][prc][mnth] = {}
                planned_target[proj][prc][mnth] = {}
                planned_prod_available_cap_point[proj][prc][mnth] = {}

    final_res = {}
    #final_res['actual_output_gross'] = actual_output_gross
    final_res['planned_output_gross'] = planned_output_gross
    #final_res['actual_prod'] = actual_prod
    # final_res['planned_prod'] = planned_prod
    # actual_targets['actual_targets'] = planned_prod
    # actual_manpower['actual_manpower'] = planned_prod
    return final_res


# current_month = datetime.strptime(mn, "%b-%y")
# previous_month = current_month - timedelta(days=2)
# prev_mnth = previous_month.strftime("%b-%y")

kwargs = {'PROJECTS':['power-players-series'],'PROCESS':['secondary','blocking'],'START':'Feb-18','END':'Aug-20'}
ob = get_all_month_data(**kwargs)
print (ob)






#print (list(set([i.month.strftime("%b-%y") for i in ScenesPlannedSecAndPoints.objects.all()])))