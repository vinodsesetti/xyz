'''COST ANALYSIS VIEWS START'''


from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny,IsAuthenticated
from main.models import *
from tracker.models import *
from tracker.converters import *
from tracker.cost_analysis_models import *
class CostAnalysis(ViewSet):
    permission_classes = [IsAuthenticated]
    def client_tbd(self,request):
        try:
            search_params = {}
            if 'project_code' in request.POST:
                search_params['fk_project__code'] = request.POST['project_code']
            main_database = ClientMainDatabase.objects.filter(**search_params)
            all_version = main_database.values('version')
            return Response({'message':'Success','main_database':main_database.values(),'all_version':all_version},status=HTTP_200_OK)
        except Exception as e:
            return Response({'message':'Failed','error_log':str(e)},status=HTTP_400_BAD_REQUEST)

    def get_project_wise_month(self,request):
        project_code = request.POST['project_code']
        project = Projects.objects.get(code=project_code)
        month_list = Converter().convert_date_range_to_months(startdate=str(project.start_date),
                                                              enddate=str(project.end_date))
        return Response({'message':'Success','month_list':month_list},status=HTTP_200_OK)

    def get_filters(self,request):
        view_name = request.POST['view_name']
        filters = {}
        if view_name in ['EIE','AAE']:
            project_list = Projects.objects.filter(category='Common').values('name', 'code')
            filters['projects'] = project_list

        if view_name in  ['EPA']:
            project_list = Projects.objects.filter(category='Common').values('name', 'code')
            filters['projects'] = project_list

        return Response({'message':"Success",'filters':filters},status=HTTP_200_OK)

    def get_project_details(self, project_code=""):
        project = Projects.objects.get(code=project_code)
        project_detail = {}
        project_detail['name'] = project.name
        project_detail['code'] = project.code
        project_detail['id'] = project.id
        project_detail['thumbnail'] = str(project.thumbnail)
        project_detail['category'] = project.category
        project_detail['start_date'] = str(project.start_date)
        project_detail['end_date'] = str(project.end_date)
        project_detail['total_episode'] = project.total_episode
        project_detail['single_episode_duration'] = project.single_episode_duration
        project_detail['resolution'] = project.resolution
        project_detail['drive_letter'] = project.drive_letter
        project_detail['network_path'] = project.network_path
        return project_detail

    def get_process_according_to_pipline(self, project_code=""):
        process_list = Processes.objects.select_related("fk_pipeline").filter(fk_project__code=project_code)
        pipeline_wise_process = {}
        for i in process_list:
            if i.fk_pipeline.name in pipeline_wise_process.keys():
                pipeline_wise_process[i.fk_pipeline.name].append(i.name)
            else:
                pipeline_wise_process[i.fk_pipeline.name] = [i.name]
        return pipeline_wise_process

    def generate_months_according_to_date_range(self, start_date=None, end_date=None):
        month_list = Converter().convert_date_range_to_months(startdate=start_date, enddate=end_date)
        return month_list

    def essential_entries(self,request):
        try:
            project_code = request.POST['project_code']
            project_detail = self.get_project_details(project_code=project_code)
            pipeline_wise_process = self.get_process_according_to_pipline(project_code=project_code)
            shedular_obj = Scheduler.objects.filter(project=project_code)
            proj_sch = shedular_obj.filter(name='PROJECT_SCH_DATES').latest('created_at')
            start_date = proj_sch.start
            end_date = proj_sch.end
            month_list = self.generate_months_according_to_date_range(start_date=project_detail['start_date'],
                                                                      end_date=project_detail['end_date'])

            process_wise_schedule_date = {i.process:{'start_date':i.start_date,'end_date':i.end_date} for i in shedular_obj.filter(name='PROCESS_SCH_DATES')}
            incentive_obj = Incentive.objects.select_related('fk_project','created_by','fk_process').filter(fk_project__code=project_code)
            data = {
                'header':{
                    'columns':[
                            {'name':'Process','subcolumns':[{'name':''}]},
                            {'name':'Start Date','subcolumns':[{'name':''}]},
                            {'name':'End Date','subcolumns':[{'name':''}]},
                            {'name':'Percentage Factor For Manweeks Estimation','subcolumns':[{'name':''}]},
                    ]+[{'name':i,'subcolumns':[{'name':''}]} for i in month_list]
                }
            }

            rows = {'data':[]}
            for i in incentive_obj:
                pass
            return Response({'message':'Success','project_datial':project_detail},status=HTTP_200_OK)
        except Exception as e:
            return Response({'message':'Something Went Wrong','error_log':str(e)},status=HTTP_200_OK)

    def asset_estimation(self,request):
        try:
            project_code = request.POST['project_code']
            cmd_obj = ClientMainDatabase.objects.get(fk_project__code=project_code)
            data = {}
            data['project'] = cmd_obj.fk_project.name
            data['each_episode_length_in_minutes'] = cmd_obj.each_episode_length_in_minutes
            data['total_number_of_episode'] = cmd_obj.total_number_of_episode
            data['sets_quantity'] = cmd_obj.sets_quantity
            data['props_quantity'] = cmd_obj.props_quantity
            data['vehicles_quantity'] = cmd_obj.vehicles_quantity
            data['chars_quantity'] = cmd_obj.chars_quantity
            data['vfx_quantity'] = cmd_obj.vfx_quantity
            data['mg_quantity'] = cmd_obj.mg_quantity
            data['no_of_2d_bg_matte'] = cmd_obj.no_of_2d_bg_matte
            data['no_shots_per_episode'] = cmd_obj.no_shots_per_episode
            data['avg_no_of_chars_per_episode'] = cmd_obj.avg_no_of_chars_per_episode
            data['total_duration_of_kf_animation_per_episode'] = cmd_obj.total_duration_of_kf_animation_per_episode
            data['project'] = cmd_obj.total_duration_of_kf_lipsync_animation_per_episode
            data['total_duration_of_kf_lipsync_animation_per_episode'] = cmd_obj.total_duration_of_vfx_per_episode
            data['total_duration_of_lit_rendering'] = cmd_obj.total_duration_of_lit_rendering
            data['total_duration_of_comp_per_episode'] = cmd_obj.total_duration_of_comp_per_episode
            data['resolution_of_final_render'] = cmd_obj.resolution_of_final_render
            data['version'] = cmd_obj.version
            asset_estimation_object = AssetEstimation.objects.select_related('fk_project','fk_process').filter(fk_project__code=project_code)
            process_list = [i.fk_process.name for i in asset_estimation_object]
            project_wise_asset_process_obj = {i.name:i for i in Processes.objects.filter(fk_project=cmd_obj.fk_project,fk_pipeline__name='asset')}
            if cmd_obj:
                for i in project_wise_asset_process_obj.keys():
                    asset_est_obj ,stta = AssetEstimation.objects.get_or_create(fk_project=cmd_obj.fk_project,fk_process=project_wise_asset_process_obj[i])
                    if i == 'modeling':
                        main_pack = asset_est_obj.main_pack_elements
                        episodic = asset_est_obj.episodic_elements
                        main_pack['PROPS']['Quantity'] = cmd_obj.props_quantity['Primary']
                        main_pack['SETS']['Quantity'] = cmd_obj.sets_quantity['Primary']
                        main_pack['CHARS']['Quantity'] = cmd_obj.chars_quantity['Primary']
                        main_pack['VEHICLES']['Quantity'] = cmd_obj.vehicles_quantity['Primary']
                        episodic['PROPS']['Quantity'] = cmd_obj.props_quantity['Primary']
                        episodic['PROPS']['Quantity'] = cmd_obj.props_quantity['Primary']
                        episodic['PROPS']['Quantity'] = cmd_obj.props_quantity['Primary']
                        episodic['PROPS']['Quantity'] = cmd_obj.props_quantity['Primary']
                        asset_est_obj.main_pack_elements = main_pack
                        asset_est_obj.episodic_elements = episodic
                        asset_est_obj.save()

            # asset_estimation_object = AssetEstimation.objects.filter(fk_project__code=project_code).values()
            return Response({'message': 'Success', 'main_database':data,'asset_estimation': asset_estimation_object.values()}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Something Went Wrong', 'error_log': str(e)}, status=HTTP_200_OK)

    def approved_asset_estimation(self,request):
        try:
            project_code = request.POST['project_code']
            process = "Rigging"
            project_detail = self.get_project_details(project_code=project_code)
            all_asset_type = AssetType.objects.filter(fk_project__code=project_code)
            data = {
                'header': {
                    'columns': [
                                   {'name': 'Asset Type', 'subcolumns': [{'name': ''}]},
                                   {'name': 'Process', 'subcolumns': [{'name': ''}]},
                                   {'name': 'Mandays / Points Per Element', 'subcolumns': [{'name': ''}]},
                                   {'name': 'Total No. Of Element', 'subcolumns': [{'name': ''}]},
                                   {'name': 'Total Budget Mandays / Per Points', 'subcolumns': [{'name': ''}]},
                               ]
                }
            }

            rows = {'data': []}
            for i in all_asset_type:
                print (i)
                data_value = []
                data_value.append({'value':i.name})
                data_value.append({'value':process})
                data_value.append({'value':0})
                data_value.append({'value':'ffff'})
                data_value.append({'value':'bbbb'})
                rows['data'].append(data_value)
            data['rows'] = rows
            return Response({'message': 'Success', 'project_datails': project_detail,'table_data':data}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Something Went Wrong', 'error_log': str(e)}, status=HTTP_200_OK)


    def approved_estimation(self,request):
        try:
            pass
        except:
            pass

    def entries_particular_scenes(self,request):
        try:
            pass
        except:
            pass




class CostAnalysisEntries(ViewSet):
    def get_project_specifications(self,project=''):
        specifications = Projects.objects.filter(code=project).values('total_episode', 'start_date', 'end_date',
                                                                      'single_episode_duration','fps')[0]
        return specifications


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

    def get_project_dates(self, request):
        try:
            project = request.POST['PROJECT']
            project_dates = Projects.objects.filter(code=project).values('start_date', 'end_date')[0]
            st_dte = str(project_dates['start_date'])
            en_dte = str(project_dates['end_date'])
            if st_dte in [None, 'None', '', ""]:
                st_dte = datetime.now().strftime("%Y-%m-%d")

            if en_dte in [None, 'None', '', ""]:
                en_dte = datetime.now().strftime("%Y-%m-%d")

            if st_dte == en_dte:
                proj_dates = [datetime.strptime(st_dte, "%Y-%m-%d").strftime("%b-%y")]
            else:
                dates = [str(st_dte), str(en_dte)]
                start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
                proj_dates = list(OrderedDict(
                    ((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys())
            proj_start = proj_dates[0]
            proj_end = proj_dates[-1]
            data = {'proj_dates': proj_dates, 'start': proj_start, 'end': proj_end}
            return Response({'data': data}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def essentials(self,request):
        try:
            project = request.POST['PROJECT']
            start = request.POST['START']
            end  = request.POST['END']
            prev_next_months = self.get_perv_next_months(start_date=start,end_date=end)

            staff_estimation = {i.staff_title: {'count': i.associate_count, 'manweeks': i.total_man_weeks,'staff_type':i.staff_type,'staff_title':i.staff_title} for i in
                                StaffEstimation.objects.filter(project__code=project)}

            specifications = Projects.objects.filter(code=project).values('total_episode', 'start_date', 'end_date',
                                                                       'single_episode_duration')[0]


            processes = Processes.objects.filter(fk_project__code=project).values_list('name', flat=True).distinct().order_by('id')


            Obj = SchedulePercentageFactors.objects.select_related('project').filter(project__code=project).order_by('pk')
            percent_factors = {}
            for i in Obj:
                sch_dt = str(i.sch_date.strftime("%b-%y"))
                st = str(i.start_date)
                en = str(i.end_date)
                if i.process in percent_factors:
                    percent_factors[i.process][sch_dt] = i.percentage_factor
                else:
                    percent_factors[i.process] = {'start': st, 'end': en, sch_dt: i.percentage_factor,
                                       'factor': i.percentage_factor_for_manweeks_estimation}

            data = {'specifications':specifications,'percent_factors':percent_factors,'staff_estimation':staff_estimation,
                    'processes':processes,'prev_next_months':prev_next_months}
            return Response({'data':data}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def particular_assets(self,request):
        try:
            project = request.POST['PROJECT']
            process = request.POST['PROCESS']
            start = request.POST['START']
            end = request.POST['END']
            st_dte = datetime.strptime(start, "%b-%y").strftime("%Y-%m-%d")
            en_dte = datetime.strptime(end, "%b-%y").strftime("%Y-%m-%d")
            prev_next_months = self.get_perv_next_months(start_date=start, end_date=end)
            obj = ParticularsAssets.objects.select_related('project').filter(project__code=project,process=process)
            final_res = {}
            total_counts = {}
            for i in obj:
                month_name = str(i.month.strftime("%b-%y"))
                asset_val = month_name+"_asset"
                points = month_name+"_points"
                if i.asset_type in final_res:
                    final_res[i.asset_type][asset_val] = i.no_of_assets
                    final_res[i.asset_type][points] = i.points_per_asset_elements
                else:
                    final_res[i.asset_type] = {'points_per_elemets':i.points_per_elemets,'total_elemets':i.total_elemets,asset_val:i.no_of_assets,
                               points:i.points_per_asset_elements}
                total_counts[i.asset_type] = total_counts.get(i.asset_type,0)+i.no_of_assets
                total_counts[i.asset_type+"_points"] = total_counts.get(i.asset_type+"_points",0)+i.points_per_asset_elements
            sub_td = ['No Of Assets','Points Per Elements']*len(prev_next_months['proj_dates'])
            dates_td = []
            prev_dates_td = []
            next_dates_td = []

            for i in prev_next_months['proj_dates']:
                dates_td.append(i+"_asset")
                dates_td.append(i+"_points")

            for i in prev_next_months['prev_dte']:
                prev_dates_td.append(i+"_asset")
                prev_dates_td.append(i+"_points")

            for i in prev_next_months['next_dte']:
                next_dates_td.append(i+"_asset")
                next_dates_td.append(i+"_points")
            data = {'data':final_res,'prev_month':prev_next_months,'sub_td':sub_td,'dates_td':dates_td,
                    'next_dates_td':next_dates_td,'prev_dates_td':prev_dates_td,'totals':total_counts}
            return Response({'data': data}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def particular_scenes(self,request):
        try:
            project = request.POST['PROJECT']
            episodes = json.loads(request.POST['EPISODES'])
            if request.POST['PROCESS'] == 'Animation':
                process = ['blocking','secondary']
            else:
                process = [request.POST['PROCESS']]

            start = request.POST['START']
            end = request.POST['END']
            prev_next_months = self.get_perv_next_months(start_date=start, end_date=end)
            project_specifications = self.get_project_specifications(project=project)
            fps = project_specifications['fps']
            ep_sec = {}
            ep_points = {}
            month_prod_info = {}
            shotObj = Shot.objects.filter(fk_project__code=project, fk_episode__name__in=episodes).exclude(frames='')
            taskObj = Tasks.objects.filter(fk_project__code=project, episode__name__in=episodes,
                                           process__name__in=process).exclude(new_complexity=-1)
            prodObj = Productivity.objects.filter(fk_task__fk_project__code=project,
                                                  fk_task__episode__name__in=episodes,
                                                  fk_task__process__name__in=process)

            for i in shotObj:
                ep_sec[i.fk_episode.name] = ep_sec.get(i.fk_episode.name, 0) + float(i.frames) / int(fps)

            for i in taskObj:
                ep_points[i.episode.name] = ep_points.get(i.episode.name, 0) + float(i.new_complexity)

            existing_shots = []
            for i in prodObj:
                prod_date = i.created_at.strftime("%b-%y")
                if i.fk_task:
                    episode = i.fk_task.episode.name
                    try:
                        if i.fk_task.fk_shot.name not in existing_shots:
                            sec = float(i.fk_task.fk_shot.frames) / int(fps)
                        else:
                            sec = 0
                    except:
                        sec = 0
                    existing_shots.append(i.fk_task.fk_shot.name)
                    try:
                        points = i.productivity
                    except:
                        points = 0

                    if episode in month_prod_info:
                        if prod_date in month_prod_info[episode]:
                            month_prod_info[episode][prod_date]['sec'] += sec
                            month_prod_info[episode][prod_date]['points'] += points
                        else:
                            month_prod_info[episode][prod_date] = {'sec': sec, 'points': points}
                    else:
                        month_prod_info[episode] = {prod_date: {'sec': sec, 'points': points}}

            st1 = datetime.strptime(start, "%b-%y").strftime("%Y-%m-%d")
            en1 = datetime.strptime(end, "%b-%y").strftime("%Y-%m-%d")
            dates = [st1, en1]
            start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
            month_names = list(OrderedDict(
                ((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys())
            month_names.append(request.POST['END'])

            scenes_data = {}
            cumulative = {'avg_prod_sec':0}
            for k, v in ep_points.items():
                scenes_data[k] = {}
                total_completed_points = 0
                total_completed_sec = 0
                for mn in month_names:
                    total_sec = round(ep_sec.get(k, 0),2)
                    total_points = round(ep_points.get(k, 0),2)
                    completed_points = 0
                    completed_sec = 0
                    pending_points = round((total_points - total_completed_points),2)
                    pending_sec = round((total_sec - total_completed_sec),2)
                    try:
                        pending_points_percent = round((pending_points / total_points) * 100,2)
                    except:
                        pending_points_percent = 0
                    try:
                        pending_sec_percent = round(((pending_sec / total_sec) * 100),2)
                    except:
                        pending_sec_percent = 0

                    completed_points = round(month_prod_info.get(k, {}).get(mn, {}).get('points', 0),2)
                    completed_sec = round(month_prod_info.get(k, {}).get(mn, {}).get('sec', 0),2)
                    total_completed_points += completed_points
                    total_completed_sec += completed_sec
                    try:
                        completed_points_percent = round(((completed_points / pending_points) * 100),2)
                    except:
                        completed_points_percent = 0
                    try:
                        completed_sec_percent = round(((completed_sec / pending_sec) * 100),2)
                    except:
                        completed_sec_percent = 0

                    if pending_points_percent == 0.00:
                        pending_points_percent = ''
                    if pending_sec_percent == 0.00:
                        pending_sec_percent = ''
                    if pending_points == 0.00:
                        pending_points = ''
                    if pending_sec == 0.00:
                        pending_sec = ''

                    if completed_sec_percent == 0.00:
                        completed_sec_percent = ''
                    if completed_points_percent == 0.00:
                        completed_points_percent = ''
                    if completed_points == 0.00:
                        completed_points = ''
                    if completed_sec == 0.00:
                        completed_sec = ''

                    scenes_data[k][mn] = {
                        'Pending': {'sec%': pending_sec_percent, 'sec': pending_sec, 'points': pending_points,
                                    'points%': pending_points_percent},
                        'Planned': {'sec%':'', 'sec':'', 'points':'', 'points%':''},
                        'Completed': {'sec%': completed_sec_percent, 'sec': completed_sec, 'points': completed_points,
                                      'points%': completed_points_percent}}
                    cumulative[mn] = {'prod_sec':0,'planned_sec':0,'planned_points':0}
            col_set_1 = ['Pending','Planned','Completed']*len(prev_next_months.get('proj_dates'))
            col_set_3 = ['Productivity Sec','Planned Sec','Planned Points']*len(prev_next_months.get('proj_dates'))
            col_set_2 = ['Sec','Sec%','Points','Points%']*(3*len(prev_next_months.get('proj_dates')))
            return Response({'data':scenes_data,'months':prev_next_months,'sec':ep_sec,'points':ep_points,
                             'episodes':episodes,'col_set_1':col_set_1,
                             'col_set_2':col_set_2,'cumulative':cumulative,'col_set_3':col_set_3,
                             'project_specifications':project_specifications}, status=HTTP_200_OK)
        except Exception as e:
            import sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Exception Line Number")
            print (e)
            print(exc_tb.tb_lineno)

            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def get_incentive_targets(self,request):
        try:
            project = request.POST['PROJECT']
            st1 = request.POST['START']
            en1 = request.POST['END']
            start = datetime.strptime(request.POST['START'],'%b-%y').strftime("%Y-%m-%d")
            end = datetime.strptime(request.POST['END'],'%b-%y').strftime("%Y-%m-%d")
            prev_next_months = self.get_perv_next_months(start_date=st1, end_date=en1)
            obj = IncentiveTargets.objects.filter(project__code=project,month__range = [start,end]).order_by('pk')
            data = {}
            for i in obj:
                mname = i.month.strftime("%b-%y")
                if i.process in data:
                    data[i.process][mname] = i.incentive_target
                    data[i.process]['total']+=i.incentive_target

                else:
                    data[i.process] = {mname: i.incentive_target,'total':i.incentive_target}
            return Response({'message': ' Successfully','data':data,'prev_next_months':prev_next_months}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_staff_estimations(self, request):
        try:
            update_data = json.loads(request.POST['est_data'])
            projObj = Projects.objects.filter(code = request.POST['PROJECT'])[0]
            for k,v in update_data.items():
                StaffEstimation.objects.get_or_create(project = projObj,staff_title =k,associate_count = v['count'],total_man_weeks=v['manweeks'])
            return Response({'message': 'Estimation Successfully Updated'}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_specifications(self, request):
        try:
            update_data = json.loads(request.POST['est_data'])
            Projects.objects.filter(code = request.POST['PROJECT']).update(total_episode = update_data['total_episode'],
                                                                          start_date=update_data['start_date'],
                                                                          end_date=update_data['end_date'],
                                                                          single_episode_duration=update_data[
                                                                              'single_episode_duration']
                                                                          )
            return Response({'message': ' Successfully Updated'}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_schedule_project_factors(self, request):
        try:
            update_data = json.loads(request.POST['est_data'])
            projObj = Projects.objects.filter(code=request.POST['PROJECT'])[0]
            for k, v in update_data.items():
                for k1,v1 in v.items():
                    if v1:
                        stdte = v['start_date']
                        endte = v['end_date']
                        data = {'project': projObj, 'process': k, 'start_date': stdte,'end_date':endte}
                        if k1 not in ['start_date','end_date']:
                            data['sch_date'] = datetime.strptime(k1,"%b-%y").strftime("%Y-%m-%d")
                            data['percentage_factor'] = v1
                            SchedulePercentageFactors.objects.get_or_create(**data)
            return Response({'message': 'Percentage Factors Successfully Updated'}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_particular_assets(self,request):
        try:
            update_data = json.loads(request.POST['est_data'])
            process = request.POST['PROCESS']
            projObj = Projects.objects.filter(code=request.POST['PROJECT'])[0]
            for k, v in update_data.items():
                month_names = list(set([i.split("_")[0] for i in v.keys()]))
                for i in month_names:
                    customObj = {'asset_type': k,'project':projObj,'process':process}
                    month_format = datetime.strptime(i, "%b-%y").strftime("%Y-%m-%d")
                    if v.get(i + "_asset"):
                        customObj['no_of_assets'] = v[i + "_asset"]
                        customObj['month'] = month_format
                    if v.get(i + "_points"):
                        customObj['points_per_asset_elements'] = v[i + "_points"]
                        customObj['month'] = month_format
                    obj = ParticularsAssets.objects.filter(project__code = request.POST['PROJECT'],process = process,month = customObj['month'],asset_type=k)
                    if obj:
                        obj.update(**customObj)
                    else:
                        ParticularsAssets.objects.get_or_create(**customObj)
            return Response({'message': ' Successfully Updated'}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_incentive_targets(self,request):
        try:
            project = request.POST['PROJECT']
            update_data = json.loads(request.POST['update_data'])
            projObj = Projects.objects.get(code=project)
            for k,v in update_data.items():
                for k1,v1 in v.items():
                    mname = datetime.strptime(k1,"%b-%y").strftime("%Y-%m-%d")
                    obj = IncentiveTargets.objects.filter(project__code=project,month=mname,process=k)
                    if obj:
                        obj.update(incentive_target = v1)
                    else:
                        IncentiveTargets.objects.create(project=projObj,month=mname, process=k,incentive_target=v1)
            return Response({'message': ' Successfully Updated'},
                            status=HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def analysis(self,request):
        try:
            project = request.POST['PROJECT']

            if request.POST['PROCESS'] == 'All Scene Processes':
                pass
            elif request.POST['PROCESS'] == 'All Asset Processes':
                process = ['modeling','texturing']

            elif request.POST['PROCESS'] == 'ALC Processes':
                pass
            else:
                process = [request.POST['PROCESS']]

            startDte = request.POST['START']
            endDte = request.POST['END']
            asset_data = {}
            asset_points = {}
            asset_upto_month = {}
            asset_points_upto_month = {}
            total_output_for_month = {}
            output_of_the_month = {}
            man_power_upto_month = {}
            prod_for_month = {}
            prod_upto_month = {}
            target_for_incentive = {}
            target_based_on_ctc = {}
            capacity = {}
            capacity_upto_month = {}
            capacity_utalization_for_month = {}
            capacity_utalization_upto_month = {}
            month_wise_attendence = {}
            month_list = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep',
                          10: 'Oct', 11: 'Nov', 12: 'Dec'}
            month_list_reverse = {'Sep': 9, 'Jan': 1, 'Apr': 4, 'May': 5, 'Nov': 11, 'Feb': 2, 'Mar': 3, 'Aug': 8,
                                  'Jul': 7, 'Oct': 10, 'Jun': 6, 'Dec': 12}
            month_end_dates = {'Sep': '30', 'Jan': '31', 'Apr': '30', 'May': '31', 'Nov': '30', 'Feb': '28',
                               'Mar': '31', 'Aug': '31', 'Jul': '31', 'Oct': '31', 'Jun': '30', 'Dec': '31'}

            prev_next_months = self.get_perv_next_months(start_date=startDte, end_date=endDte)
            dates = [datetime.strptime(startDte, "%b-%y").strftime("%Y-%m-%d"),
                     datetime.strptime(endDte, "%b-%y").strftime("%Y-%m-%d")]
            start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
            all_month_names = list(OrderedDict(
                ((start + timedelta(_)).strftime(r"%b-%y"), None) for _ in range((end - start).days)).keys()) + [endDte]

            for i in ParticularsAssets.objects.select_related('project').filter(project__code=project,
                                                                                process__in=process).values():
                month_name = i['month'].strftime("%b-%y")
                all_month_names.append(month_name)

                if i['process'] in asset_data:
                    if i['asset_type'] in asset_data[i['process']]:
                        asset_data[i['process']][i['asset_type']][month_name] = i['no_of_assets']
                    else:
                        asset_data[i['process']][i['asset_type']] = {month_name: i['no_of_assets']}
                else:
                    asset_data[i['process']] = {i['asset_type']: {month_name: i['no_of_assets']}}

                if i['process'] in asset_points:
                    if i['asset_type'] in asset_points[i['process']]:
                        asset_points[i['process']][i['asset_type']][month_name] = i['points_per_asset_elements']
                    else:
                        asset_points[i['process']][i['asset_type']] = {month_name: i['points_per_asset_elements']}
                else:
                    asset_points[i['process']] = {i['asset_type']: {month_name: i['points_per_asset_elements']}}

            for k, v in asset_data.items():
                asset_upto_month[k] = {}
                for k1, v1 in v.items():
                    asset_upto_month[k][k1] = {}
                    existing_month_val = 0
                    for i in all_month_names:
                        asset_upto_month[k][k1][i] = existing_month_val + v1.get(i, 0)
                        existing_month_val += v1.get(i, 0)

            for k, v in asset_points.items():
                asset_points_upto_month[k] = {}
                for k1, v1 in v.items():
                    asset_points_upto_month[k][k1] = {}
                    existing_month_val = 0
                    for i in all_month_names:
                        asset_points_upto_month[k][k1][i] = existing_month_val + v1.get(i, 0)
                        existing_month_val += v1.get(i, 0)

            for k, v in asset_points.items():
                total_output_for_month[k] = {}
                for k1, v1 in v.items():
                    for k2, v2 in v1.items():
                        if k2 in total_output_for_month[k]:
                            total_output_for_month[k][k2] += v2
                        else:
                            total_output_for_month[k][k2] = v2

            for k, v in total_output_for_month.items():
                output_of_the_month[k] = {}
                existing_val = 0
                for k1, v1 in v.items():
                    output_of_the_month[k][k1] = existing_val + v1
                    existing_val += v1

            attendence_obj = GatewayDailyAttandance.objects.values('created_at__month', 'created_at__year','process').annotate(
                count=Count('fk_user')).filter(count__gt=1, project=project, process__in=process)

            current_manpower = 0
            for i in attendence_obj:
                month_name = "{0}-{1}".format(month_list.get(i['created_at__month']), str(i['created_at__year'])[2:])
                man_power = round(float(i['count'] / 21.65), 2)
                if i['process'] in month_wise_attendence:
                    month_wise_attendence[i['process']][month_name] = man_power
                else:
                    month_wise_attendence[i['process']] = {month_name: man_power}

            for k, v in month_wise_attendence.items():
                man_power_upto_month[k] = {}
                current_month_val = 0
                for i in all_month_names:
                    man_power_upto_month[k][i] = current_month_val + v.get(i, 0)
                    current_month_val += v.get(i, 0)

            for i in process:
                prod_for_month[i] = {}
                for mnth in all_month_names:
                    try:
                        prod_for_month[i][mnth] = total_output_for_month.get(i, {}).get(mnth,
                                                                                        0) / month_wise_attendence.get(
                            k, {}).get(mnth, 0)
                    except:
                        prod_for_month[i][mnth] = 0

            for k, v in prod_for_month.items():
                prod_upto_month[k] = {}
                current_val = 0
                for i in all_month_names:
                    prod_upto_month[k][i] = current_val + v.get(i, 0)
                    current_val += v.get(i, 0)

            st = datetime.strptime(startDte, "%b-%y").strftime("%Y-%m-%d")
            en = datetime.strptime(endDte, "%b-%y").strftime("%Y-%m-") + month_end_dates.get(endDte.split("-")[0])
            worked_artist_names = GatewayDailyAttandance.objects.values('fk_user__employee_id', 'created_at__month',
                                                                        'created_at__year','process').annotate(
                count=Count('fk_user')).filter(project=project, process__in=process, created_at__range=[st, en])
            month_wise_logged_in_artists = {}

            for i in worked_artist_names:
                month_name = "{0}-{1}".format(month_list.get(i['created_at__month']), str(i['created_at__year'])[2:])
                if i['process'] in month_wise_logged_in_artists:
                    if month_name in month_wise_logged_in_artists[i['process']]:
                        month_wise_logged_in_artists[i['process']][month_name].append(i['fk_user__employee_id'])
                    else:
                        month_wise_logged_in_artists[i['process']][month_name] = [i['fk_user__employee_id']]
                else:
                    month_wise_logged_in_artists[i['process']] = {month_name: [i['fk_user__employee_id']]}

            for k, v in month_wise_logged_in_artists.items():
                target_based_on_ctc[k] = {}
                target_for_incentive[k] = {}
                for k1, v1 in v.items():
                    month = month_list_reverse.get(k1.split("-")[0])
                    year = '20' + k1[-2:]
                    total_month_target = round(sum([float(i.actual_month_target) for i in
                                                    MonthlyTarget.objects.filter(month__month=month, month__year=year,
                                                                                 fk_user__employee_id__in=list(
                                                                                     set(v1)))]), 2)
                    target_based_on_ctc[k][k1] = total_month_target
                    target_for_incentive[k][k1] = total_month_target

            for k, v in target_based_on_ctc.items():
                capacity[k] = {}
                for k1, v1 in v.items():
                    capacity[k][k1] = target_based_on_ctc.get(k, {}).get(k1, 0) + target_for_incentive.get(k, {}).get(k1, 0)

            for k, v in capacity.items():
                val = 0
                capacity_upto_month[k] = {}
                for k1, v1 in v.items():
                    capacity_upto_month[k][k1] = val + v1
                    val += v1

            for prc in process:
                capacity_utalization_for_month[prc] = {}
                for mn in all_month_names:
                    try:
                        capacity_utalization_for_month[prc][mn] = total_output_for_month.get(prc, {}).get(mn,0) / capacity.get(prc, {}).get(mn, 0)
                    except:
                        capacity_utalization_for_month[prc][mn] = 0

            for k, v in capacity_utalization_for_month.items():
                val = 0
                capacity_utalization_upto_month[k] = {}
                for k1, v1 in v.items():
                    capacity_utalization_upto_month[k][k1] = val + v1
                    val += v1

            FinalObj = {'asset_types': asset_data, 'asset_points': asset_points,
                        'asset_types_upto_month': asset_upto_month,
                        'asset_points_upto_month': asset_points_upto_month, 'output_of_the_month': output_of_the_month,
                        'total_output_for_month': total_output_for_month, 'man_power_upto_month': man_power_upto_month,
                        'manpower_for_the_month': month_wise_attendence, 'prod_for_month': prod_for_month,
                        'prod_upto_month': prod_upto_month, 'target_based_on_ctc': target_based_on_ctc,
                        'target_for_incentive': target_for_incentive, 'capacity': capacity,
                        'capacity_upto_month': capacity_upto_month,
                        'capacity_utalization_upto_month': capacity_utalization_upto_month,
                        'capacity_utalization_for_month': capacity_utalization_for_month}

            return Response({'message': ' Success','data':FinalObj,'prev_next_months':prev_next_months}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

class CostAnalysisReports(ViewSet):
    def get_shot_asset_processes(self,request):
        try:
            obj = Processes.objects.filter(fk_project__code=request.POST['PROJECT'])
            processObj = {}
            for i in obj:
                if i.fk_pipeline.name in processObj:
                    processObj[i.fk_pipeline.name].append(i.name)
                else:
                    processObj[i.fk_pipeline.name] = [i.name]
            return Response({'message': ' Success','data':processObj}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def approved_asset_estimation(self,request):
        try:
            search_params = {}
            project = request.POST['PROJECT']
            search_params['project__code'] = project
            if 'PROCESS' in request.POST:
                process = json.loads(request.POST['PROCESS'])
                search_params['process__in'] = process
            query_obj = ApprovedAssetsEstimation.objects.filter(**search_params).values()
            data = {}
            for i in query_obj:
                if i['process'] in data:
                    data[i['process']].append(i)
                else:
                    data[i['process']] = [i]
            return Response({'message': ' Success','data':data}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_approved_asset_estimation(self,request):
        try:
            update_data = json.loads(request.POST['update_data'])
            for k,v in update_data.items():
                ApprovedAssetsEstimation.objects.filter(id=k).update(**v)
            return Response({'message': ' Successfully Updated',}, status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def approved_scene_estimation(self,request):
        try:
            project = request.POST['PROJECT']
            project_info = Projects.objects.get(code=project)
            total_asset_manweeks = sum([i.mandays_for_element*i.total_element  for i in ApprovedAssetsEstimation.objects.filter(project__code=project)])/5
            app_estimation = ApprovedEstimation.objects.filter(project__code=project)
            process_multiplier_set = {'lip_sync':0.8,'vfx':0.8,'hair_sim':0.7}
            est_data = []
            cumulative_total_manweeks = 0

            for i in app_estimation:
                ep_duration = float(project_info.single_episode_duration)
                total_ep = float(project_info.total_episode)
                prc_mul = float(process_multiplier_set.get(i.process,1))
                total_man_weeks = ((ep_duration*60*total_ep*prc_mul)/i.avg_prod_sec_per_month)*4.33
                est_data.append({'process':i.process,'avg_prod':i.avg_prod_sec_per_month,'total_man_weeks':total_man_weeks,'id':i.id})
                cumulative_total_manweeks+=total_man_weeks

            staff_estimation = {}
            for i in StaffEstimation.objects.filter(project__code=project):
                staff_estimation[i.staff_title] = {'count': i.associate_count, 'manweeks': i.total_man_weeks, 'staff_type': i.staff_type,'staff_title': i.staff_title}
                cumulative_total_manweeks+=i.total_man_weeks
            return Response({'message': ' Success','data':staff_estimation,'est_data':est_data,
                             'assets':total_asset_manweeks,'total':cumulative_total_manweeks}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def update_approved_estimation(self,request):
        try:
            update_data = json.loads(request.POST['update_data'])
            for k,v in update_data.items():
                ApprovedEstimation.objects.filter(pk=k).update(**v)
            return Response({'message': ' Successfully Updated',}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)




class AnalysisView(ViewSet):

    def get_inputs(self,request):
        project = request.POST['PROJECT']

        if request.POST['PROCESS'] == 'All Scene Processes':
            process = list(Processes.objects.filter(fk_project__code= project,fk_pipeline__name='shot').values_list('name',flat=True).distinct())
            prc_type = 'shot'
        elif request.POST['PROCESS'] == 'All Asset Processes':
            process = list(Processes.objects.filter(fk_project__code= project,fk_pipeline__name='asset').values_list('name',flat=True).distinct())
            prc_type = 'asset'

        elif request.POST['PROCESS'] == 'ALC Processes':
            process = ['blocking','secondary','lighting','comp']
            prc_type = 'shot'
        else:
            process = [request.POST['PROCESS']]
            prc_type = Processes.objects.filter(name=process[0])[0].fk_pipeline.name


        startDte = request.POST['START']
        endDte = request.POST['END']

        month_list = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep',
                      10: 'Oct', 11: 'Nov', 12: 'Dec'}
        month_list_reverse = {'Sep': 9, 'Jan': 1, 'Apr': 4, 'May': 5, 'Nov': 11, 'Feb': 2, 'Mar': 3, 'Aug': 8,
                              'Jul': 7, 'Oct': 10, 'Jun': 6, 'Dec': 12}
        month_end_dates = {'Sep': '30', 'Jan': '31', 'Apr': '30', 'May': '31', 'Nov': '30', 'Feb': '28',
                           'Mar': '31', 'Aug': '31', 'Jul': '31', 'Oct': '31', 'Jun': '30', 'Dec': '31'}

        particular_asset_params = {'project__code':project,'process__in':process}
        attendence_params = {'count__gt':1, 'project':project, 'process__in':process}


        projObj = Projects.objects.get(code=project)
        fps = int(projObj.fps)
        input_data = {'project':project,'process':process,'start':startDte,'end':endDte,'month_list':month_list,
                      'month_end_dates':month_end_dates,'month_list_reverse':month_list_reverse,
                      'particular_asset_params':particular_asset_params,'attendence_params':attendence_params,
                      'prc_type':prc_type,'fps':fps,}

        return input_data

    def get_all_month_names_in_given_range(self,start_date='',end_date=''):
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

        data = {'all_dates': proj_dates, 'prev_dte': prev_dte, 'next_dte': next_dte}
        return data

    def get_asset_information(self,params={}):
        asset_data = {}
        asset_points = {}
        for i in ParticularsAssets.objects.select_related('project').filter(**params).values():
            month_name = i['month'].strftime("%b-%y")
            if i['process'] in asset_data:
                if i['asset_type'] in asset_data[i['process']]:
                    asset_data[i['process']][i['asset_type']][month_name] = i['no_of_assets']
                    asset_data[i['process']][i['asset_type']]['total'] += i['no_of_assets']
                else:
                    asset_data[i['process']][i['asset_type']] = {month_name: i['no_of_assets'],'total':i['no_of_assets']}
            else:
                asset_data[i['process']] = {i['asset_type']: {month_name: i['no_of_assets'],'total':i['no_of_assets']}}


            if i['process'] in asset_points:
                if i['asset_type'] in asset_points[i['process']]:
                    asset_points[i['process']][i['asset_type']][month_name] = i['points_per_asset_elements']
                    asset_points[i['process']][i['asset_type']]['total'] += i['points_per_asset_elements']
                else:
                    asset_points[i['process']][i['asset_type']] = {month_name: i['points_per_asset_elements'],'total':i['points_per_asset_elements']}
            else:
                asset_points[i['process']] = {i['asset_type']: {month_name: i['points_per_asset_elements'],'total':i['points_per_asset_elements']}}

        return {'asset_data':asset_data,'asset_points':asset_points}

    def get_asset_upto_month(self,asset_data={},all_month_names=[]):
        asset_upto_month = {}
        for k, v in asset_data.items():
            asset_upto_month[k] = {}
            for k1, v1 in v.items():
                asset_upto_month[k][k1] = {'total':0}
                existing_month_val = 0
                for i in all_month_names:
                    asset_upto_month[k][k1][i] = existing_month_val + v1.get(i, 0)
                    asset_upto_month[k][k1]['total']+=existing_month_val + v1.get(i, 0)
                    existing_month_val += v1.get(i, 0)
        return asset_upto_month

    def get_asset_points_upto_month(self,asset_points={},all_month_names=[]):
        asset_points_upto_month = {}
        for k, v in asset_points.items():
            asset_points_upto_month[k] = {}
            for k1, v1 in v.items():
                asset_points_upto_month[k][k1] = {}
                existing_month_val = 0
                for i in all_month_names:
                    asset_points_upto_month[k][k1][i] = existing_month_val + v1.get(i, 0)
                    existing_month_val += v1.get(i, 0)
        return asset_points_upto_month

    def get_total_output_for_month(self,asset_points={}):
        total_output_for_month = {}
        for k, v in asset_points.items():
            total_output_for_month[k] = {'total':0}
            for k1, v1 in v.items():
                for k2, v2 in v1.items():
                    total_output_for_month[k]['total'] += v2
                    if k2 in total_output_for_month[k]:
                        total_output_for_month[k][k2] += v2
                    else:
                        total_output_for_month[k][k2] = v2
        return total_output_for_month

    def get_output_for_month(self,total_output_for_month={}):
        output_of_the_month = {}
        for k, v in total_output_for_month.items():
            output_of_the_month[k] = {'total':0}
            existing_val = 0
            for k1, v1 in v.items():
                output_of_the_month[k][k1] = existing_val + v1
                output_of_the_month[k]['total']+=existing_val + v1
                existing_val += v1
        return output_of_the_month

    def get_month_wise_attendence(self,params={},month_list={}):
        month_wise_attendence = {}
        attendence_obj = GatewayDailyAttandance.objects.values('created_at__month', 'created_at__year',
                                                               'process').annotate(
            count=Count('fk_user')).filter(**params)

        current_manpower = 0
        for i in attendence_obj:
            month_name = "{0}-{1}".format(month_list.get(i['created_at__month']), str(i['created_at__year'])[2:])
            man_power = round(float(i['count'] / 21.65), 2)
            if i['process'] in month_wise_attendence:
                month_wise_attendence[i['process']][month_name] = man_power
                month_wise_attendence[i['process']]['total']+= man_power
            else:
                month_wise_attendence[i['process']] = {month_name: man_power,'total':man_power}
        return month_wise_attendence

    def get_manpower_upto_month(self,month_wise_attendence = {},all_month_names= []):
        man_power_upto_month = {}
        for k, v in month_wise_attendence.items():
            man_power_upto_month[k] = {'total':0}
            current_month_val = 0
            for i in all_month_names:
                man_power_upto_month[k][i] = current_month_val + v.get(i, 0)
                man_power_upto_month[k]['total']+= current_month_val + v.get(i, 0)
                current_month_val += v.get(i, 0)
        return man_power_upto_month

    def get_producitivity_for_month(self,process=[],all_month_names=[],total_output_for_month={},month_wise_attendence={}):
        prod_for_month = {}
        for i in process:
            prod_for_month[i] = {'total':0}
            for mnth in all_month_names:
                try:
                    val = total_output_for_month.get(i, {}).get(mnth,0) / month_wise_attendence.get(i, {}).get(mnth, 0)
                    prod_for_month[i][mnth] = val
                    prod_for_month['total']+=val
                except:
                    prod_for_month[i][mnth] = 0
        return prod_for_month

    def get_productivity_upto_month(self,prod_for_month={},all_month_names = []):
        prod_upto_month = {}
        for k, v in prod_for_month.items():
            prod_upto_month[k] = {'total':0}
            current_val = 0
            for i in all_month_names:
                prod_upto_month[k][i] = current_val + v.get(i, 0)
                prod_upto_month[k]['total']+= current_val + v.get(i, 0)
                current_val += v.get(i, 0)
        return prod_upto_month

    def get_target_based_on_ctc_incentive(self,startDte = '',endDte='',month_end_dates='',project='',process=[],
                                          month_list=[],month_list_reverse={}):
        target_based_on_ctc = {}
        target_for_incentive = {}
        st = datetime.strptime(startDte, "%b-%y").strftime("%Y-%m-%d")
        en = datetime.strptime(endDte, "%b-%y").strftime("%Y-%m-") + month_end_dates.get(endDte.split("-")[0])
        worked_artist_names = GatewayDailyAttandance.objects.values('fk_user__employee_id', 'created_at__month',
                                                                    'created_at__year', 'process').annotate(
            count=Count('fk_user')).filter(project=project, process__in=process, created_at__range=[st, en])
        month_wise_logged_in_artists = {}

        for i in worked_artist_names:
            month_name = "{0}-{1}".format(month_list.get(i['created_at__month']), str(i['created_at__year'])[2:])
            if i['process'] in month_wise_logged_in_artists:
                if month_name in month_wise_logged_in_artists[i['process']]:
                    month_wise_logged_in_artists[i['process']][month_name].append(i['fk_user__employee_id'])
                else:
                    month_wise_logged_in_artists[i['process']][month_name] = [i['fk_user__employee_id']]
            else:
                month_wise_logged_in_artists[i['process']] = {month_name: [i['fk_user__employee_id']]}


        for k, v in month_wise_logged_in_artists.items():
            target_based_on_ctc[k] = {'total':0}
            target_for_incentive[k] = {'total':0}
            for k1, v1 in v.items():
                month = month_list_reverse.get(k1.split("-")[0])
                year = '20' + k1[-2:]
                total_month_target = round(sum([float(i.actual_month_target) for i in
                                                MonthlyTarget.objects.filter(month__month=month, month__year=year,
                                                                             fk_user__employee_id__in=list(
                                                                                 set(v1)))]), 2)
                target_based_on_ctc[k][k1] = total_month_target
                target_for_incentive[k][k1] = total_month_target
                target_based_on_ctc[k]['total']+=total_month_target
                target_for_incentive[k]['total']+=total_month_target


        return {'target_based_on_ctc':target_based_on_ctc,'target_for_incentive':target_for_incentive}

    def get_capacity(self,target_based_on_ctc={},target_for_incentive={}):
        capacity = {}
        for k, v in target_based_on_ctc.items():
            capacity[k] = {'total':0}
            for k1, v1 in v.items():
                val = target_based_on_ctc.get(k, {}).get(k1, 0) + target_for_incentive.get(k, {}).get(k1, 0)
                capacity[k][k1] = val
                capacity[k]['total']+= val
        return capacity

    def get_capacity_upto_month(self,capacity={}):
        capacity_upto_month = {}
        for k, v in capacity.items():
            val = 0
            capacity_upto_month[k] = {'total':0}
            for k1, v1 in v.items():
                capacity_upto_month[k][k1] = val + v1
                capacity_upto_month[k]['total']+=val + v1
                val += v1
        return capacity_upto_month

    def get_capacity_utalization_for_month(self,all_month_names = {},process=[],total_output_for_month={},capacity={}):
        capacity_utalization_for_month = {}
        for prc in process:
            capacity_utalization_for_month[prc] = {'total':0}
            for mn in all_month_names:
                try:
                    val = total_output_for_month.get(prc, {}).get(mn,0) / capacity.get(prc, {}).get(mn, 0)
                    capacity_utalization_for_month[prc][mn] = val
                    capacity_utalization_for_month[prc]['total']+=val
                except:
                    capacity_utalization_for_month[prc][mn] = 0
        return capacity_utalization_for_month

    def capacity_utalization_upto_month(self,capacity_utalization_for_month = {}):
        capacity_utalization_upto_month = {}
        for k, v in capacity_utalization_for_month.items():
            val = 0
            capacity_utalization_upto_month[k] = {'total':0}
            for k1, v1 in v.items():
                capacity_utalization_upto_month[k][k1] = val + v1
                capacity_utalization_upto_month[k]['total']+=val + v1
                val += v1
        return capacity_utalization_upto_month

    def get_scene_output_for_month_gross(self, startDte='', endDate='', month_end_dates={}, process=[], project='', fps=25):
        st = datetime.strptime(startDte, '%b-%y').strftime("%Y-%m-%d")
        en = datetime.strptime(endDate, '%b-%y').strftime("%Y-%m-") + month_end_dates.get(endDate.split("-")[0])
        prodObj = Productivity.objects.select_related('fk_task', 'fk_task__fk_project', 'fk_task__process').filter(
            fk_task__fk_project__code=project, fk_task__process__name__in=process, created_at__range=[st, en])
        output_for_month_gross = {}
        for i in prodObj:
            month = i.created_at.strftime("%b-%y")
            try:
                frames = float(i.fk_task.fk_shot.frames) / int(fps)
            except:
                frames = 0

            if i.fk_task.process.name in output_for_month_gross:
                if month in output_for_month_gross[i.fk_task.process.name]:
                    output_for_month_gross[i.fk_task.process.name][month] += frames
                else:
                    output_for_month_gross[i.fk_task.process.name][month] = frames
            else:
                output_for_month_gross[i.fk_task.process.name] = {month: frames}

        return output_for_month_gross

    def get_scene_output_for_the_month(self, output_month_gross={}):
        output_for_the_month = {}
        for k, v in output_month_gross.items():
            output_for_the_month[k] = {}
            for k1, v1 in v.items():
                output_for_the_month[k][k1] = float(v1 / 60)
        return output_for_the_month

    def get_scene_output_upto_month(self, output_for_the_month={}):
        output_upto_month = {}
        for k, v in output_for_the_month.items():
            output_upto_month[k] = {}
            val = 0
            for k1, v1 in v.items():
                output_upto_month[k][k1] = val + v1
                val += 0
        return output_upto_month

    def get_scene_output_for_the_month_take_one_80_percent(self, output_month_gross={}):
        output_for_the_month_take_one_80_percent = {}
        for k, v in output_month_gross.items():
            output_for_the_month_take_one_80_percent[k] = {}
            for k1, v1 in v.items():
                output_for_the_month_take_one_80_percent[k][k1] = float(v1 * 0.8)
        return output_for_the_month_take_one_80_percent

    def get_scene_output_for_the_month_take_one_20_percent(self, output_month_gross={}, output_for_month_80_percent={}):
        output_for_the_month_take_one_20_percent = {}
        for k, v in output_month_gross.items():
            output_for_the_month_take_one_20_percent[k] = {}
            for k1, v1 in v.items():
                output_for_the_month_take_one_20_percent[k][k1] = output_month_gross[k][k1] - \
                                                                  output_for_month_80_percent[k][k1]
        return output_for_the_month_take_one_20_percent

    def get_scene_output_upto_month_final(self, output_month_gross={}):
        output_upto_month_final = {}
        for k, v in output_month_gross.items():
            output_upto_month_final[k] = {}
            val = 0
            for k1, v1 in v.items():
                output_upto_month_final[k][k1] = val + v1
                val += v1
        return output_upto_month_final

    def get_scene_prod_for_available_capacity(self, outout_for_month_gross={}, manpower_for_month={}):
        prod_for_available_capacity = {}
        for k,v in outout_for_month_gross.items():
            prod_for_available_capacity[k] = {}
            for k1,v1 in v.items():
               try:
                    prod_for_available_capacity[k][k1] = v1/manpower_for_month.get(k,{}).get(k1,0)
               except:
                   prod_for_available_capacity[k][k1] = 0

        return prod_for_available_capacity

    def get_scene_prod_upto_month(self,output_upto_month_final = {},manpower_upto_month={}):
        scene_prod_upto_mnth = {}
        for k,v in output_upto_month_final.items():
            scene_prod_upto_mnth[k] = {}
            for k1,v1 in v.items():
                try:
                    scene_prod_upto_mnth[k][k1] = v1/manpower_upto_month.get(k,{}).get(k1,0)
                except:
                    scene_prod_upto_mnth[k][k1] = 0

        return scene_prod_upto_mnth

    def get_scene_seconds(self,output_for_month_gross={},capacity={}):
        get_scene_sec = {}
        for k,v in output_for_month_gross.items():
            get_scene_sec[k] = {}
            for k1,v1 in v.items():
                try:
                    get_scene_sec[k][k1] = v1/capacity.get(k,{}).get(k1,0)
                except:
                    get_scene_sec[k][k1] = 0

        return get_scene_sec

    def get_scene_points_per_episode(self,scene_sec  = {}):
        points_per_ep = {}
        value = 720
        for k,v in scene_sec.items():
            points_per_ep[k] = {}
            for k1,v1 in v.items():
                try:
                    points_per_ep[k][k1] = value/v1
                except:
                    points_per_ep[k][k1] = 0
        return points_per_ep

    def get_scene_output_for_month_points(self,output_for_month_gross={},sec_points={}):
        output_for_month = {}
        for k,v in output_for_month_gross.items():
            output_for_month[k] = {}
            for k1,v1 in v.items():
                try:
                    output_for_month[k][k1] = v1/sec_points.get(k,{}).get(k1,0)
                except:
                    output_for_month[k][k1] = 0
        return sec_points

    def get_scene_output_upto_month_points(self,output_for_month_points = {}):
        output_upto_month = {}
        for k, v in output_for_month_points.items():
            output_upto_month[k] = {}
            val = 0
            for k1, v1 in v.items():
                output_upto_month[k][k1] = val + v1
                val += 0
        return output_upto_month

    def scene_capcity_utalization(self,output_for_month_points = {},capacity={}):
        capacity_utalization = {}
        for k,v in output_for_month_points.items():
            capacity_utalization[k] = {}
            for k1,v1 in v.items():
                try:
                    capacity_utalization[k][k1] = v1/capacity.get(k,{}).get(k1,0)
                except:
                    capacity_utalization[k][k1] = 0

        return capacity_utalization

    def scene_capcity_utalization_upto_month(self,cap_utalization = {}):
        cap_utalization_upto_month = {}
        for k, v in cap_utalization.items():
            cap_utalization_upto_month[k] = {}
            val = 0
            for k1, v1 in v.items():
                cap_utalization_upto_month[k][k1] = val + v1
                val += 0
        return cap_utalization_upto_month

    def scene_main_block(self,request):
        input_data = self.get_inputs(request)
        monthnames = self.get_all_month_names_in_given_range(start_date=input_data['start'], end_date=input_data['end'])
        output_for_month_gross = self.get_scene_output_for_month_gross(startDte=input_data['start'],
                                                                       endDate=input_data['end'],
                                                                       month_end_dates=input_data['month_end_dates'],
                                                                       process=input_data['process'],
                                                                       project=input_data['project'], fps=input_data['fps'])

        output_for_the_month = self.get_scene_output_for_the_month(output_month_gross=output_for_month_gross)

        output_upto_month = self.get_scene_output_upto_month(output_for_the_month = output_for_the_month)
        output_for_the_month_take_one_80_percent = self.get_scene_output_for_the_month_take_one_80_percent(
            output_month_gross=output_for_month_gross)
        output_for_the_month_take_one_20_percent = self.get_scene_output_for_the_month_take_one_20_percent(
            output_month_gross=output_for_month_gross,
            output_for_month_80_percent=output_for_the_month_take_one_80_percent)
        output_upto_month_final = self.get_scene_output_upto_month_final(output_month_gross=output_for_month_gross)

        month_wise_attendence = self.get_month_wise_attendence(params=input_data['attendence_params'],
                                                               month_list=input_data['month_list'])
        prod_for_available_capacity_points = self.get_scene_prod_for_available_capacity(outout_for_month_gross=output_for_month_gross,
                                                                                        manpower_for_month=month_wise_attendence)

        man_power_upto_month = self.get_manpower_upto_month(month_wise_attendence=month_wise_attendence,all_month_names=monthnames['all_dates'])

        prod_upto_month  = self.get_scene_prod_upto_month(output_upto_month_final =output_upto_month_final,manpower_upto_month=man_power_upto_month)


        get_targets = self.get_target_based_on_ctc_incentive(startDte=input_data['start'], endDte=input_data['end'],
                                                             month_end_dates=input_data['month_end_dates'],
                                                             project=input_data['project'],
                                                             process=input_data['process'],
                                                             month_list=input_data['month_list'],
                                                             month_list_reverse=input_data['month_list_reverse'])
        capacity = self.get_capacity(target_based_on_ctc=get_targets['target_based_on_ctc'],
                                     target_for_incentive=get_targets['target_for_incentive'])
        capacity_upto_month = self.get_capacity_upto_month(capacity=capacity)

        scene_seconds = self.get_scene_seconds(output_for_month_gross=output_for_month_gross,capacity=capacity)
        points_per_episode = self.get_scene_points_per_episode(scene_sec  =scene_seconds)

        output_for_month_points = self.get_scene_output_for_month_points(output_for_month_gross=output_for_month_gross,sec_points=scene_seconds)
        output_upto_month_points = self.get_scene_output_upto_month_points(output_for_month_points =output_for_month_points )

        capacity_utalization_for_month = self.scene_capcity_utalization(output_for_month_points = output_for_month_points,capacity=capacity)
        cap_utalization_upto_month = self.scene_capcity_utalization_upto_month(cap_utalization=capacity_utalization_for_month)

        prod_for_points = {}
        schedule_take_one_end = {}
        schedule_take_final_end = {}
        prod_upto_month_for_available_capacity = {}
        FinalObj = {'output_for_month_gross': output_for_month_gross, 'output_for_the_month': output_for_the_month,
                    'output_for_the_month_take_one_80_percent': output_for_the_month_take_one_80_percent,
                    'output_for_the_month_take_one_20_percent': output_for_the_month_take_one_20_percent,
                    'output_upto_month_final': output_upto_month_final,
                    'prod_for_available_capacity_points': prod_for_available_capacity_points,
                    'manpower_for_the_month':month_wise_attendence,'man_power_upto_month':man_power_upto_month,
                    'output_upto_month':output_upto_month,'prod_upto_month':prod_upto_month,
                    'target_based_on_ctc': get_targets['target_based_on_ctc'],
                    'target_for_incentive': get_targets['target_for_incentive'], 'capacity': capacity,
                    'capacity_upto_month': capacity_upto_month,'scene_seconds':scene_seconds,
                    'points_per_episode':points_per_episode,'output_for_month_points':output_for_month_points,
                    'output_upto_month_points':output_upto_month_points,
                    'capacity_utalization_for_month':capacity_utalization_for_month,
                    'capacity_utalization_upto_month':cap_utalization_upto_month,'prod_for_points':prod_for_points,
                    'schedule_take_one_end':schedule_take_one_end,
                    'schedule_take_final_end':schedule_take_final_end,
                    'prod_upto_month_for_available_capacity':prod_upto_month_for_available_capacity,
                    }

        return {'data': FinalObj, 'prev_next_months': monthnames,'process':input_data['process']}
        # return Response({'message': ' Successfully Updated', 'data': FinalObj, 'prev_next_months': monthnames,
        #                  'prc_type': input_data['prc_type']}, status=HTTP_200_OK)

    def asset_main_block(self,request):
        try:
            input_data = self.get_inputs(request)
            monthnames = self.get_all_month_names_in_given_range(start_date=input_data['start'],end_date=input_data['end'])
            asset_information = self.get_asset_information(input_data['particular_asset_params'])
            asset_upto_month = self.get_asset_upto_month(asset_data=asset_information['asset_data'],all_month_names=monthnames['all_dates'])
            asset_points_upto_month = self.get_asset_points_upto_month(asset_points=asset_information['asset_points'],all_month_names=monthnames['all_dates'])
            total_output_for_month = self.get_total_output_for_month(asset_points=asset_information['asset_points'])
            month_wise_attendence = self.get_month_wise_attendence(params=input_data['attendence_params'],month_list=input_data['month_list'])
            man_power_upto_month = self.get_manpower_upto_month(month_wise_attendence = month_wise_attendence,all_month_names=monthnames['all_dates'])
            prod_for_month = self.get_producitivity_for_month(process=input_data['process'],all_month_names=monthnames['all_dates'],
                                                              total_output_for_month = total_output_for_month,month_wise_attendence=month_wise_attendence)
            prod_upto_month = self.get_productivity_upto_month(prod_for_month=prod_for_month,all_month_names=monthnames['all_dates'])

            get_targets = self.get_target_based_on_ctc_incentive(startDte = input_data['start'],endDte=input_data['end'],
                                                                 month_end_dates=input_data['month_end_dates'],
                                                                 project=input_data['project'],process=input_data['process'],
                                                                month_list=input_data['month_list'],month_list_reverse=input_data['month_list_reverse'])
            capacity = self.get_capacity(target_based_on_ctc=get_targets['target_based_on_ctc'],target_for_incentive=get_targets['target_for_incentive'])
            capacity_upto_month = self.get_capacity_upto_month(capacity=capacity)
            capacity_utalization_for_month = self.get_capacity_utalization_for_month(all_month_names =monthnames['all_dates'],process=input_data['process'],
                                                                                     total_output_for_month=total_output_for_month,
                                                                                     capacity=capacity)
            capacity_utalization_upto_month = self.capacity_utalization_upto_month(capacity_utalization_for_month = capacity_utalization_for_month)
            output_of_the_month = self.get_output_for_month(total_output_for_month=total_output_for_month)
            FinalObj = {'asset_types': asset_information['asset_data'], 'asset_points': asset_information['asset_points'],
                        'asset_types_upto_month': asset_upto_month,
                        'asset_points_upto_month': asset_points_upto_month, 'output_of_the_month': output_of_the_month,
                        'total_output_for_month': total_output_for_month, 'man_power_upto_month': man_power_upto_month,
                        'manpower_for_the_month': month_wise_attendence, 'prod_for_month': prod_for_month,
                        'prod_upto_month': prod_upto_month, 'target_based_on_ctc': get_targets['target_based_on_ctc'],
                        'target_for_incentive': get_targets['target_for_incentive'], 'capacity': capacity,
                        'capacity_upto_month': capacity_upto_month,
                        'capacity_utalization_upto_month': capacity_utalization_upto_month,
                        'capacity_utalization_for_month': capacity_utalization_for_month}
            return {'data': FinalObj, 'prev_next_months': monthnames,'process':input_data['process']}
            #return Response({'message': ' Successfully Updated','data':FinalObj,'prev_next_months':monthnames,'prc_type':input_data['prc_type']}, status=HTTP_200_OK)
        except Exception as e:
            print (e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)

    def analysis_main_block(self,request):
        type_of_prc = self.get_inputs(request)['prc_type']
        if type_of_prc == 'shot':
            obj = self.scene_main_block(request)
        elif type_of_prc == 'asset':
            obj = self.asset_main_block(request)
        else:
            obj = {'data':{}, 'prev_next_months':{},'prc_type':{},'process':{}}

        return Response({'message': 'Success','data':obj['data'], 'prev_next_months':obj['prev_next_months'],
                             'prc_type':type_of_prc,'process':obj['process']}, status=HTTP_200_OK)


class SummerySheet(ViewSet):

    def get_asset_man_weeks(self,project=''):
        asset_man_weeks = {}
        for i in ApprovedAssetsEstimation.objects.filter(project__code=project):
            val = i.mandays_for_element * i.total_element
            asset_man_weeks[i.process] = asset_man_weeks.get(i.process,0)+val
        return asset_man_weeks

    def get_scene_man_weeks(self,projObj={},project=''):
        scene_man_weeks = {}
        app_estimation = ApprovedEstimation.objects.filter(project__code=project)
        process_multiplier_set = {'lip_sync': 0.8, 'vfx': 0.8, 'hair_sim': 0.7}
        for i in app_estimation:
            ep_duration = float(projObj.single_episode_duration)
            total_ep = float(projObj.total_episode)
            prc_mul = float(process_multiplier_set.get(i.process, 1))
            total_man_weeks = ((ep_duration * 60 * total_ep * prc_mul) / i.avg_prod_sec_per_month) * 4.33
            scene_man_weeks[i.process] = scene_man_weeks.get(i.process,0)+total_man_weeks
        return scene_man_weeks

    def get_month_wise_attendence(self,project=''):
        month_wise_attendence = {}
        attendence_obj = GatewayDailyAttandance.objects.values('process').annotate(count=Count('fk_user')).filter(project=project)
        for i in attendence_obj:
            man_power = round(float(i['count'] / 21.65), 2)
            month_wise_attendence[i['process']] =month_wise_attendence.get(i['process'],0)+man_power
        return month_wise_attendence

    def get_target_based_on_ctc_incentive(self,project=''):
        target_based_on_ctc = {}
        target_for_incentive = {}
        worked_artist_names = GatewayDailyAttandance.objects.values('fk_user__employee_id', 'created_at__month',
                                                                    'created_at__year', 'process').annotate(
            count=Count('fk_user')).filter(project=project)
        month_wise_logged_in_artists = {}

        for i in worked_artist_names:
            if i['process'] in month_wise_logged_in_artists:
                month_wise_logged_in_artists[i['process']].append(i['fk_user__employee_id'])
            else:
                month_wise_logged_in_artists[i['process']] = [i['fk_user__employee_id']]


        for k, v in month_wise_logged_in_artists.items():
            target_based_on_ctc[k] = {}
            target_for_incentive[k] = {}
            total_month_target = 0
            for i in MonthlyTarget.objects.filter(fk_user__employee_id__in=list(set(v))):
                if i.actual_month_target not in ['N/A','',' ',None,'None']:
                    total_month_target+=float(i.actual_month_target)
            target_based_on_ctc[k] = total_month_target
            target_for_incentive[k] = total_month_target
        return {'target_based_on_ctc':target_based_on_ctc,'target_for_incentive':target_for_incentive}

    def get_capacity(self,target_based_on_ctc={},target_for_incentive={}):
        capacity = {}
        for k, v in target_based_on_ctc.items():
            val = target_based_on_ctc.get(k,0) + target_for_incentive.get(k,0)
            capacity[k] = val
        return capacity

    def get_asset_points(self,project = ''):
        asset_points = {}
        for i in ParticularsAssets.objects.select_related('project').filter(project__code=project).values():
            asset_points[i['process']] = asset_points.get(i['process'],0)+i['points_per_asset_elements']
        return asset_points

    def get_producitivity_for_month(self,process=[],all_month_names=[],total_output_for_month={},month_wise_attendence={}):
        prod_for_month = {}
        for i in process:
            prod_for_month[i] = {'total':0}
            for mnth in all_month_names:
                try:
                    val = total_output_for_month.get(i, {}).get(mnth,0) / month_wise_attendence.get(i, {}).get(mnth, 0)
                    prod_for_month[i][mnth] = val
                    prod_for_month['total']+=val
                except:
                    prod_for_month[i][mnth] = 0
        return prod_for_month

    def get_productivity_upto_month(self,prod_for_month={},all_month_names = []):
        prod_upto_month = {}
        for k, v in prod_for_month.items():
            prod_upto_month[k] = {'total':0}
            current_val = 0
            for i in all_month_names:
                prod_upto_month[k][i] = current_val + v.get(i, 0)
                prod_upto_month[k]['total']+= current_val + v.get(i, 0)
                current_val += v.get(i, 0)
        return prod_upto_month



    def get_summery(self,request):
        try:
            project = request.POST['PROJECT']
            projObj = Projects.objects.get(code=project)
            process = list(Processes.objects.filter(fk_project__code=project).values_list('name',flat=True))
            total_duration = float(projObj.single_episode_duration)*float(projObj.total_episode)
            asset_man_weeks = self.get_asset_man_weeks(project = project)
            scene_man_weeks = self.get_scene_man_weeks(projObj = projObj,project=project)
            process_multiplier_set = {'lip_sync': 0.8, 'vfx': 0.8, 'hair_sim': 0.7}
            asset_man_weeks.update(scene_man_weeks)
            all_process_man_weeks = asset_man_weeks
            manpower_for_the_month = self.get_month_wise_attendence(project=project)
            get_targets = self.get_target_based_on_ctc_incentive(project=project)
            capacity = self.get_capacity(target_based_on_ctc=get_targets['target_based_on_ctc'],target_for_incentive=get_targets['target_for_incentive'])
            asset_points = self.get_asset_points(project = project)
            obj = {}
            for i in process:
                try:
                    app_avg_prod = round(float((total_duration/all_process_man_weeks.get(i,0))*process_multiplier_set.get(i,1)*4.33),2)
                except:
                    app_avg_prod = 0

                try:
                    app_capacity = capacity.get(i,0)/manpower_for_the_month.get(i,0)
                except:
                    app_capacity = 0

                try:
                    app_availble_avg_prod =  (app_capacity/21.65)*app_avg_prod
                except:
                    app_availble_avg_prod = 0

                try:
                    app_available_total_man_weeks = all_process_man_weeks/(app_capacity/21.65)
                except:
                    app_available_total_man_weeks = 0

                ex_avg_prod = 0
                ex_total_man_weeks = 0
                ex_capacity = 0
                ex_availble_avg_prod = 0
                ex_available_total_man_weeks = 0
                obj[i] = {'app_avg_prod':app_avg_prod,'app_total_man_weeks':all_process_man_weeks.get(i,0),
                          'app_capacity':app_capacity,'app_availble_avg_prod':app_availble_avg_prod,
                          'app_available_total_man_weeks':app_available_total_man_weeks,
                          'ex_avg_prod':ex_avg_prod,'ex_total_man_weeks':ex_total_man_weeks,
                          'ex_availble_avg_prod':ex_availble_avg_prod,'ex_available_total_man_weeks':ex_available_total_man_weeks,
                          'ex_capacity':ex_capacity
                          }
            return Response({'message': 'Success', 'data': obj,},
                                status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=HTTP_400_BAD_REQUEST)


            # for prc in process:
        #



class MonthlySummery(ViewSet):
    '''
        project wise report
        --------------------
        prod for 21.65 points/month = output for month gross/capacity
        For Scenes
        ---------
        output for month gross = productivity sec in a given date range
        capacity = target based on ctc+target based on incentive
    '''

    def scenes_output_for_the_month_gross(self,month='',year='',project='',fps=25,scene_process = []):
        '''output for the month gross means productive sec i.e fk__task__shot__frames/fps'''
        params = {'fk_task__fk_project__code':project,'created_at__month':month,'created_at__year':year,'fk_task__process__name__in':scene_process}
        req_cols = ('fk_task__process__name','productivity','fk_task__fk_shot__frames')
        select_related_cols = ('fk_task','fk_task__fk_project','fk_task__process__name', 'productivity','fk_task__fk_shot__frames')
        prodObj = Productivity.objects.select_related(*select_related_cols).filter(**params).values(*req_cols)
        output_gross_sec = {}
        for i in prodObj:
            prc = i['fk_task__process__name']
            if prc in ['blocking','secondary']:
                prc = 'Animation'
            frames = i['fk_task__fk_shot__frames']
            if frames not in [None,'None','']:
                output_gross_sec[prc] = output_gross_sec.get(prc,0)+(float(frames)/fps)
        return output_gross_sec

    def get_target_based_on_ctc_incentive(self,project='',month='',year='',scene_process = []):
        target_based_on_ctc = {}
        target_for_incentive = {}
        worked_artist_names = GatewayDailyAttandance.objects.select_related('fk_user').values('fk_user__employee_id','process').annotate(count=Count('fk_user')).filter(project=project,created_at__month=month,created_at__year=year)
        month_wise_logged_in_artists = {}
        for i in worked_artist_names:
            if i['process'] in month_wise_logged_in_artists:
                month_wise_logged_in_artists[i['process']].append(i['fk_user__employee_id'])
            else:
                month_wise_logged_in_artists[i['process']] = [i['fk_user__employee_id']]

        for k, v in month_wise_logged_in_artists.items():
            if k in ['blocking','secondary']:
                k = 'Animation'
            target_based_on_ctc[k] = {}
            target_for_incentive[k] = {}
            total_month_target = 0
            for i in MonthlyTarget.objects.select_related('fk_user').filter(fk_user__employee_id__in=list(set(v))):
                if i.actual_month_target not in ['N/A','',' ',None,'None']:
                    total_month_target+=float(i.actual_month_target)

            target_based_on_ctc[k] = total_month_target
            target_for_incentive[k] = total_month_target

        return {'target_based_on_ctc':target_based_on_ctc,'target_for_incentive':target_for_incentive}

    def get_capacity(self,target_based_on_ctc={},target_for_incentive={},scene_process = []):
        capacity = {}
        for k, v in target_based_on_ctc.items():
            val = target_based_on_ctc.get(k,0) + target_for_incentive.get(k,0)
            capacity[k] = val
        return capacity

    def get_attendence(self,month='',year='',project='',scene_process = []):
        params = {'project':project,'created_at__month':month,'created_at__year':year,'count__gt':1}
        AttendenceObj = GatewayDailyAttandance.objects.values('process').annotate(count=Count('fk_user')).filter(**params)
        process_wise_attendence = {}
        for i in AttendenceObj:
            if i['process'] in ['secondary','blocking']:
                prc = 'Animation'
            else:
                prc = i['process']
            process_wise_attendence[prc] = i['count']
        return process_wise_attendence
    def capacity_utalization_scenes(self,output_for_month={},capacity={},scene_process = []):
        '''capacity_utalization = output_for_month/capacity
        output_for_month = output_for_gross/sec_per_point
        sec_per_point = output_for_gross/capacity'''
        capacity_utalization = {}
        for i in scene_process:
            try:
                capacity_utalization[i] = (output_for_month.get(i,0)/(output_for_month.get(i,0)/capacity.get(i,0)))/capacity.get(i,0)
            except:
                capacity_utalization[i] = 0.0
        return capacity_utalization


    def get_scene_man_weeks(self,projObj={},project='',scene_process = []):
        scene_man_weeks = {}
        app_estimation = ApprovedEstimation.objects.filter(project__code=project)
        process_multiplier_set = {'lip_sync': 0.8, 'vfx': 0.8, 'hair_sim': 0.7}
        for i in app_estimation:
            if i.process in ['secondary','blocking']:
                prc = 'Animation'
            else:
                prc = i.process
            ep_duration = float(projObj.single_episode_duration)
            total_ep = float(projObj.total_episode)
            prc_mul = float(process_multiplier_set.get(prc, 1))
            total_man_weeks = ((ep_duration * 60 * total_ep * prc_mul) / i.avg_prod_sec_per_month) * 4.33
            scene_man_weeks[prc] = scene_man_weeks.get(prc,0)+total_man_weeks
        return scene_man_weeks


    def get_productivity_for_scenes(self,capacity_data={},output_for_month={},attendence={},cap_utalization={},scene_man_weeks={},scene_process = []):
        '''
            productivity = output_for_month_gross/capacity
            output = output_for_month_gross
            man_month = attendence
            capacity_utalization = capacity_utalization
            productivity_upto_month = ''
            avg_prod_per_month = scene_man_weeks (# formula =  (total_duration/total_man_weeks)*4.33 #)
            planned_vs_expected_upto_one_month = productivity/avg_prod_per_month

        '''


        summery = {}
        for i in scene_process:
            try:
                prod = (output_for_month.get(i,0)/capacity_data.get(i,0))*21.65
            except:
                prod = 0.0
            try:
                capacity =output_for_month.get(i,0)/attendence.get(i,0)
            except:
                capacity =0.0

            output = output_for_month.get(i,0)
            man_month = attendence.get(i,0)
            capacity_utalization=cap_utalization.get(i,0)
            try:
                upto_month = prod/scene_man_weeks.get(i,0)
            except:
                upto_month = 0.0

            upto_month = upto_month*100
            projected = upto_month

            summery[i] = {'prod':prod,'capacity':capacity,'output':output,'man_month':man_month,'capacity_utalization':capacity_utalization,
                          'upto_month':upto_month,'projected':projected}

        return summery


    def get_productivity_for_assets(self,project='',month='',attendence = {},asset_process=[],capacity_data = {}):
        ''' assets points from particular assets feedded from entries
        productivity = total output for month/manpower for the month
        '''

        summery = {}
        assetsObj = ParticularsAssets.objects.values('process').annotate(count = Sum('points_per_asset_elements')).filter(project__code=project,month=month)
        total_output_for_month = {i['process']:i['count'] for i in assetsObj}
        for i in asset_process:
            try:
                prod = total_output_for_month.get(i,0)/attendence.get(i,0)
            except:
                prod =0

            capacity = prod
            output = total_output_for_month.get(i,0)
            man_month = attendence.get(i,0)
            try:
                capacity_utalization = total_output_for_month.get(i,0)/capacity_data.get(i,0)
            except:
                capacity_utalization = 0.0
            upto_month = 0.0
            projected = 0.0
            summery[i] = {'prod': prod, 'capacity': capacity, 'output': output, 'man_month': man_month,
                          'capacity_utalization': capacity_utalization,
                          'upto_month': upto_month, 'projected': projected}
        return summery


    def get_project_wise_report(self,request):
        project = request.POST['PROJECT']
        month = request.POST['MONTH']
        month_list = {'Sep': 9, 'Jan': 1, 'Apr': 4, 'May': 5, 'Nov': 11, 'Feb': 2, 'Mar': 3, 'Aug': 8,
                      'Jul': 7, 'Oct': 10, 'Jun': 6, 'Dec': 12}
        month_name = month_list[month.split("-")[0]]
        year_name = "20{0}".format(month.split("-")[1])
        ProjObj = Projects.objects.get(code=project)
        fps = int(ProjObj.fps)
        asset_prc = list(Processes.objects.filter(fk_project__code=project,fk_pipeline__name='asset').values_list('name', flat=True).distinct())
        scene_prc = list(Processes.objects.filter(fk_project__code=project,fk_pipeline__name='shot').values_list('name', flat=True).distinct())
        scene_output_month_gross = self.scenes_output_for_the_month_gross(month=month_name,year=year_name,project=project,fps=fps,scene_process=scene_prc)
        target_and_incentives = self.get_target_based_on_ctc_incentive(month=month_name,year=year_name,project=project,scene_process=scene_prc)
        targets = target_and_incentives['target_based_on_ctc']
        incentives = target_and_incentives['target_for_incentive']
        capacity = self.get_capacity(target_based_on_ctc=targets,target_for_incentive=incentives,scene_process=scene_prc)
        scene_cap_utalization = self.capacity_utalization_scenes(output_for_month=scene_output_month_gross,
                                                                 capacity=capacity,scene_process=scene_prc)

        attendence = self.get_attendence(month=month_name, year=year_name, project=project,scene_process=scene_prc)
        scene_man_weeks = self.get_scene_man_weeks(projObj=ProjObj,project=project,scene_process=scene_prc)
        prod_scenes = self.get_productivity_for_scenes(capacity_data=capacity, output_for_month=scene_output_month_gross,
                                                       cap_utalization=scene_cap_utalization,attendence=attendence,scene_man_weeks = scene_man_weeks,scene_process=scene_prc)
        prod_assets = self.get_productivity_for_assets(project=project,month=datetime.strptime(month, '%b-%y').strftime(
                                                                        "%Y-%m-%d"),attendence = attendence,asset_process=asset_prc,capacity_data=capacity)
        prod_scenes.update(prod_assets)

        FinalObj = {}
        for k,v in prod_scenes.items():
            units = 'Points'
            if k in ['Animation','comp','lighting']:
                units = 'Sec'
            FinalObj[k] = {'units':units,'actual':{'prod':v,'capacity':0.0,'manpower':0.0,'capacity_utalization':0.0,'upto_month':0.0,'for_projected':0.0},'planned':{'prod':0.0,'capacity':0.0,'manpower':0.0,'capacity_utalization':0.0,'upto_month':0.0,'for_projected':0.0}}
        return Response({'message': 'Success', 'data': FinalObj,},status=HTTP_200_OK)

    def get_process_wise_report(self,request):
        pass


    def get_manpower_wise_report(self,request):
        pass



class GetHostName(ViewSet):
    def get_host_details(self,request):
        print (request.META['COMPUTERNAME'])
        print (request.META)
        return Response({'message':'success'},status=HTTP_200_OK)


class AnalysisScenes(ViewSet):

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

    def get_output_for_month_actual(self,**kwargs):
        '''
            outpuput for the month calculation same for both completed and coming months
            output_for_the_month = output_for_month_gross_sec/sec_per_point
            sec_per_points = gross/capacity
            output_for_month_gross_sec = plannedOutputSecs Updated By PM in PARTICULAR SCENES (planned sec)
            Database Table : ScenesPlannedSecAndPoints
            Columns: planned_sec

        '''
        final_res = {}
        actual_output_for_month_gross = kwargs['OUTPUT_FOR_MONTH_GROSS']
        actual_targets = kwargs['ACTUAL_TARGETS']
        for proj in kwargs['PROJECTS']:
            final_res[proj] = {}
            for prc in kwargs['PROCESS']:
                if prc in ['blocking','secondary']:
                    prc ='Animation'
                final_res[proj][prc] = {}
                for mn in kwargs['ALL_MONTHS']['proj_dates']:
                    gross = actual_output_for_month_gross.get(proj,{}).get(prc,{}).get(mn,0)
                    capacity = actual_targets.get(proj,{}).get(prc,{}).get(mn,0)
                    try:
                        sec_per_points = gross/target
                    except:
                        sec_per_points = 0

                    try:
                        val = gross/sec_per_points
                    except:
                        val = 0
                    final_res[proj][prc][mn] = val
        return final_res

    def get_output_for_the_month(self,gross = {},target={}):
        actual = self.get_output_for_month_actual(gross=gross['ACTUAL'],target=target)
        planned = self.get_output_for_month_planned(gross=gross['PLANNED'],target=target)
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
                    #print ("******"*10)

                    planned_capacity[proj][prc][mn] = planned_capacity_points
                    planned_capacity_target_manpower_obj[proj][prc][mn] = {'planned_capacity':planned_capacity_points,
                                                                           'planned_manpower':planned_manpower,
                                                                           'planned_target':planned_target}

        return {'all_data': planned_capacity_target_manpower_obj, 'planned_capacity': planned_capacity}

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
        params = {'PROJECTS':kwargs['PROJECTS'],'PROCESS':kwargs['PROCESS'],'ALL_MONTHS':kwargs['ALL_MONTHS'],
                  'ACTUAL':kwargs['MANPOWER_FOR_THE_MONTH']['actual'],'PLANNED':kwargs['OUTPUT_FOR_MONTH_GROSS']['planned'],
                  'COL_NAME':'output_for_month'}
        upto_month = self.get_generic_upto_month_function(**params)

    def get_generic_analysis_stats_for_all_reports(self,**kwargs):
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
        #output_for_the_month = self.get_output_for_the_month(gross = output_for_the_month_gross,target = targets)
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
        analysis_report['capacity_upto_month'] = capacity_upto_month

        return analysis_report

    def get_anlysis_report(self,request):
        params = {'PROJECT':[request.POST['PROJECT']],'PROCESS':request.POST['PROCESS'],'START':request.POST['START'],
                  'END': request.POST['END']}
        analysis_stats = self.get_generic_analysis_stats_for_all_reports(**params)
        # obj = {'output_for_the_month_gross':analysis_stats['output_for_the_month_gross'],'completed':analysis_stats['completed'],
        #        'coming':analysis_stats['coming'],'output_upto_month':analysis_stats['output_upto_month'],
        #        }
        obj = {'output_for_the_month_gross':analysis_stats['output_for_the_month_gross'],'completed':analysis_stats['completed'],
               'coming':analysis_stats['coming'],'output_upto_month':analysis_stats['output_upto_month'],
               'manpower_for_the_month':analysis_stats['manpower_for_the_month'],
               'manpower_upto_month':analysis_stats['manpower_upto_month'],
               'targets':analysis_stats['targets'],
               'prod_available_capacity_points':analysis_stats['prod_available_capacity_points'],
               'prod_for_the_month_planned':analysis_stats['prod_for_month_planned']}
        return Response({'message': 'Success', 'data': obj,},status=HTTP_200_OK)



'''COST ANALYSIS VIEWS END'''




'''COST ANALYSIS MODELS START'''

from django.db import models
from django.contrib.postgres.fields import JSONField,ArrayField
from main.models import *
from django.utils import timezone

class ClientMainDatabase(models.Model):
    fk_project = models.ForeignKey(Projects,null=False,blank=False,on_delete=models.CASCADE)
    each_episode_length_in_minutes = models.CharField(max_length=10,blank=True,null=True)
    total_number_of_episode = models.CharField(max_length=10,blank=True,null=True)
    sets_quantity = JSONField(default={"Primary":0,"Secondary":0,"Incidental":0})
    props_quantity = JSONField(default={"Primary":0,"Secondary":0,"Incidental":0})
    vehicles_quantity = JSONField(default={"Primary":0,"Secondary":0,"Incidental":0})
    chars_quantity = JSONField(default={"Primary":0,"Secondary":0,"Incidental":0})
    vfx_quantity = JSONField(default={"Primary":0,"Secondary":0,"Incidental":0})
    mg_quantity = JSONField(default={"Primary":0,"Secondary":0,"Incidental":0})
    no_of_2d_bg_matte = models.CharField(max_length=20,blank=True,null=True)
    no_shots_per_episode = models.CharField(max_length=10,null=True,blank=True)
    avg_no_of_chars_per_episode =  models.CharField(max_length=10,null=True,blank=True)
    total_duration_of_kf_animation_per_episode =  models.CharField(max_length=10,null=True,blank=True)
    total_duration_of_kf_lipsync_animation_per_episode =  models.CharField(max_length=10,null=True,blank=True) #90% of episode duration
    total_duration_of_vfx_per_episode =  models.CharField(max_length=10,null=True,blank=True) #35% of episode duration
    total_duration_of_lit_rendering =  models.CharField(max_length=10,null=True,blank=True)
    total_duration_of_comp_per_episode =  models.CharField(max_length=10,null=True,blank=True)
    resolution_of_final_render =  models.CharField(max_length=20,null=True,blank=True)
    version = models.CharField(max_length=10,blank=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)

class AssetEstimation(models.Model):
    fk_project = models.ForeignKey(Projects,null=False,blank=False,on_delete=models.CASCADE)
    fk_process = models.ForeignKey(Processes,null=False,blank=False,on_delete=models.CASCADE)
    schedule_weeks = models.CharField(max_length=30,blank=True,null=True)
    man_power_requirement = models.CharField(max_length=30,blank=True,null=True)
    man_month_per_episode = models.CharField(max_length=30,blank=True,null=True)
    asset_participation_type = models.CharField(max_length=30,choices=(
        ('MAIN_PACK','MAIN_PACK'),
        ('EPISODIC','EPISODIC')
    ),null=False,blank=False
                                                )
    main_pack_elements = JSONField(default={"PROPS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "SETS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "CHARS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "VEHICLES":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "MG":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "VFX":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "MATTE":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "ANIMALS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "UV":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0}})

    episodic_elements = JSONField(default={"PROPS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "SETS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "CHARS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "VEHICLES":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "MG":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "VFX":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "MATTE":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "ANIMALS":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0},
                                            "UV":{"Quantity":0,"Mandays_Per_Element":0,"Manweeks_Per_Episode":0,"Total_Manweeks":0}})
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)

class ParticularsAssets(models.Model):
    project = models.ForeignKey(Projects,null=True, blank=True, on_delete=models.CASCADE)
    process = models.CharField(max_length=50, blank=True, null=True)
    asset_type = models.CharField(max_length=50, blank=True, null=True)
    points_per_elemets = models.FloatField(default=0.0)
    total_elemets = models.IntegerField(default=0)
    month = models.DateField(blank=True, null=True)
    no_of_assets = models.IntegerField(default=0)
    points_per_asset_elements= models.FloatField(max_length=50,default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)

class ParticularsScenes(models.Model):
    project = models.ForeignKey(Projects,null=True, blank=True, on_delete=models.CASCADE)
    process = models.CharField(max_length=50, blank=True, null=True)
    episode = models.CharField(max_length=50, blank=True, null=True)
    sec_budget = models.FloatField(default=0.0)
    points_budget = models.FloatField(default=0.0)
    output_for_the_month_gross = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)


class ScenesPlannedSecAndPoints(models.Model):
    project = models.ForeignKey(Projects,null=True, blank=True, on_delete=models.CASCADE)
    process = models.CharField(max_length=50, blank=True, null=True)
    planned_prod = models.FloatField(default=0.0)
    planned_sec = models.FloatField(default=0.0)
    planned_points = models.FloatField(default=0.0)
    month = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)



class ApprovedAssetsEstimation(models.Model):
    project = models.ForeignKey(Projects,null=True, blank=True, on_delete=models.CASCADE)
    process = models.CharField(max_length=50, blank=True, null=True)
    asset_type = models.CharField(max_length=50, blank=True, null=True)
    mandays_for_element = models.FloatField(default=0.0)
    total_element = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)

class ApprovedEstimation(models.Model):
    project = models.ForeignKey(Projects,null=True, blank=True, on_delete=models.CASCADE)
    process = models.CharField(max_length=50, blank=True, null=True)
    avg_prod_sec_per_month = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)

class IncentiveTargets(models.Model):
    project = models.ForeignKey(Projects,null=True, blank=True, on_delete=models.CASCADE)
    process = models.CharField(max_length=50, blank=True, null=True)
    month = models.DateField(blank=True, null=True)
    incentive_target = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now_add=True)


'''COST ANALYYS MODELS END'''


'''TRACKER MODELS START'''

from django.db import models
from django.contrib.postgres.fields import JSONField,ArrayField
from main.models import *
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.db import transaction
from tracker.triggers import *
from django.utils import timezone
from .cost_analysis_models import *
import  calendar
from datetime import timedelta,date

class Team(models.Model):
    fk_user = models.ForeignKey(User,null=False,blank=False,related_name="user",on_delete=models.DO_NOTHING)
    superior = models.ForeignKey(User,null=True,blank=True,related_name="superior",on_delete=DO_NOTHING)
    supervisor = models.ForeignKey(User,null=True,blank=True,related_name='supervisor',on_delete=models.DO_NOTHING)
    manager = models.ForeignKey(User,null=True,blank=True,related_name='manager',on_delete=models.DO_NOTHING)
    pa = models.ForeignKey(User,null=True,blank=True,related_name='pa',on_delete=models.DO_NOTHING)
    pc = models.ForeignKey(User,null=True,blank=True,related_name='pc',on_delete=models.DO_NOTHING)
    project_hr = models.ForeignKey(User,blank=True,null=True,related_name="project_hr",on_delete=DO_NOTHING)
    active = models.BooleanField(default=True)

class ProjectWiseAuthority(models.Model):
    fk_project = models.ForeignKey(Projects,blank=True,null=True,on_delete=DO_NOTHING)
    fk_user = models.ForeignKey(User, blank=False,null=False,on_delete=DO_NOTHING)
    role = models.CharField(max_length=30,blank=False,null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)


class SupervisorWiseArtist(models.Model):
    artist = models.ForeignKey(User,related_name='art',null=False,blank=True,on_delete=models.CASCADE)
    supervisor = models.ForeignKey(User,related_name='super',null=False,blank=True,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)


class AssetType(models.Model):
    name = models.CharField(max_length=50,blank=False,null=False)
    fk_project = models.ForeignKey(Projects, null=False, blank=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DummyProcess(models.Model):
    name = models.CharField(max_length=100,default='N/A')
    pipeline = models.ForeignKey(Pipeline,null=False,blank=False,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)


class Shot(models.Model):
    name = models.CharField(max_length=500,blank=False,null=False,db_index=True)
    serial_no = models.IntegerField(blank=True, null=True)
    frames = models.CharField(max_length=500, null=True, blank=True)
    sequence = models.CharField(max_length=500,blank=True,null=True)
    sets = ArrayField(models.TextField(),blank=True,null=True)
    props = ArrayField(models.TextField(),blank=True,null=True)
    vehicles = ArrayField(models.TextField(),blank=True,null=True)
    vfx = ArrayField(models.TextField(),blank=True,null=True)
    mg = ArrayField(models.TextField(),blank=True,null=True)
    chars = ArrayField(models.TextField(),blank=True,null=True)
    animals = ArrayField(models.TextField(),blank=True,null=True)
    setprops = ArrayField(models.TextField(),blank=True,null=True)
    description = models.TextField()
    is_keyshot = models.BooleanField(default=False,null=True,blank=True)
    parent_shot = models.CharField(max_length=500,blank=True,null=True)
    child_shot = models.CharField(max_length=500,blank=True,null=True)
    unique_shot = models.BooleanField(default=False,null=True,blank=True)
    fk_episode = models.ForeignKey(Episodes,blank=False,null=False,on_delete=models.CASCADE)
    fk_project = models.ForeignKey(Projects, null=False, blank=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    name = models.CharField(max_length=500,blank=False)
    serial_no = models.IntegerField(blank=True, null=True)
    asset_type = models.ForeignKey(AssetType,blank=True,null=True,on_delete=models.CASCADE)
    fk_episode = models.ForeignKey(Episodes, blank=False, null=False,on_delete=models.CASCADE)
    fk_project = models.ForeignKey(Projects, null=False, blank=True,on_delete=models.CASCADE)
    client_naming = models.CharField(max_length=500,blank=True,null=True)
    client_notes = models.TextField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    design_pack = models.TextField(blank=True,null=True)
    input_date = models.DateTimeField(blank=True, null=True)
    upload_date = models.DateTimeField(blank=True, null=True)
    final_app_date = models.DateTimeField(blank=True, null=True)
    final_app_image = models.CharField(max_length=500,blank=True, null=True)
    final_app_file_path = models.CharField(max_length=500,blank=True, null=True)
    final_app_mov = models.CharField(max_length=500,blank=True, null=True)
    custom_col_1 = models.CharField(max_length=500,blank=True, null=True)
    custom_col_2 = models.CharField(max_length=500,blank=True, null=True)
    custom_col_3 = models.CharField(max_length=500,blank=True, null=True)
    client_status = models.TextField(blank=True, null=True)

    scope = models.CharField(blank=True,default="N",null=True,max_length=10)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    # ===================
    input_md = models.CharField(max_length=100,blank=True, null=True)
    input_tx = models.CharField(max_length=100,blank=True, null=True)
    input_rg = models.CharField(max_length=100,blank=True, null=True)
    input_ML = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.name

class Tasks(models.Model):
    name = models.CharField(max_length=255,default="N/A")
    fk_project = models.ForeignKey(Projects, null=True, blank=True,on_delete=models.CASCADE)
    episode = models.ForeignKey(Episodes,null=True,blank=True,on_delete=models.CASCADE)
    process = models.ForeignKey(Processes,blank=True,null=True,on_delete=models.CASCADE)
    fk_shot = models.ForeignKey(Shot,null=True,blank=True,on_delete=models.CASCADE)
    fk_asset = models.ForeignKey(Asset,null=True,blank=True,on_delete=models.CASCADE)
    pipeline_type = models.CharField(max_length=25,default="N/A")
    process_name = models.CharField(max_length=25,default="N/A")
    panel_complexity = models.FloatField(max_length=50,default=-1.0)    #have Same Value
    new_complexity = models.FloatField(max_length=50,default=-1.0)      #have Same Value
    complexity_grade = models.CharField(blank=True,null=True,max_length=10,default="N/A")
    new_complexity_grade = models.CharField(blank=True,null=True,max_length=10,default="N/A")
    production_done = models.BooleanField(default=False)
    month_cycle = models.CharField(max_length=50,default="N/A",blank=True,null=True)
    i_count = models.IntegerField(default=1)
    e_count = models.IntegerField(default=1)
    in_hand = models.CharField(max_length=15,default="False")
    status = models.CharField(max_length=100,default="Unassigned")
    ch_status = models.CharField(max_length=50,default="Y2C")
    bg_status = models.CharField(max_length=50,default="Y2C")
    mg_status = models.CharField(max_length=50,default="Y2C")
    fx_status = models.CharField(max_length=50,default="Y2C")
    render_paths = ArrayField(models.TextField(),blank=True,null=True)
    is_green_shot = models.BooleanField(default=False)
    supervisor = models.ForeignKey(User,null=True,blank=True,related_name="Supervisor",on_delete=models.DO_NOTHING)
    assigned = models.ForeignKey(User,null=True,blank=True,related_name="Assigned",on_delete=models.DO_NOTHING)
    creative_director = models.ForeignKey(User,null=True,blank=True,related_name="Creative_Director",on_delete=models.DO_NOTHING)
    manager = models.ForeignKey(User,null=True,blank=True,related_name="TaskManager",on_delete=models.DO_NOTHING)
    client = models.ForeignKey(User,null=True,blank=True, related_name="Client",on_delete=models.DO_NOTHING)
    panel_remarks = models.TextField(null=True,blank=True,default="N/A")
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ReviewTask(models.Model):
    fk_task = models.ForeignKey("Tasks",blank=False,null=False,on_delete=models.CASCADE)
    status = models.CharField(max_length=30,default="Assignment")
    review_type = models.CharField(max_length=30)
    is_note = models.BooleanField(default=False)
    review_timestamp = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

class RetakeTypeTags(models.Model):
    retake_type = models.CharField(max_length=200,null=False,blank=False)
    fk_review_task = models.ForeignKey('ReviewTask',null=True,blank=True,on_delete=models.CASCADE)
    extra_note = models.TextField()
    created_at = models.DateTimeField(timezone.now)
    

class StatusLog(models.Model):
    to_status = models.CharField(max_length=50,blank=False,null=False)
    from_status = models.CharField(max_length=50,blank=False,null=False)
    fk_task = models.ForeignKey('Tasks',blank=False,null=False,on_delete=models.CASCADE)
    created_for = models.ForeignKey(User,related_name="created_for",blank=True,null=True,on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now,max_length=50,blank=False,null=False)
    created_by = models.ForeignKey(User,blank=False,null=False,on_delete=models.DO_NOTHING)


class MonthlyTarget(models.Model):
    fk_user = models.ForeignKey(User,related_name='for_user',blank=False,null=False,on_delete=DO_NOTHING)
    month = models.DateField()
    actual_month_target = models.CharField(max_length=30,blank=False,null=False,default='N/A')
    backlog = models.CharField(max_length=30,blank=False,null=False,default='N/A')
    month_target_backlog = models.CharField(max_length=30,blank=False,null=False,default='N/A')
    updated_by = models.ForeignKey(User,related_name='updated_by',blank=False,null=False,on_delete=DO_NOTHING)
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)


class AssignmentLog(models.Model):
    to_artist = models.ForeignKey(User,blank=True,null=True,related_name="to_artist",on_delete=models.DO_NOTHING)
    from_artist = models.ForeignKey(User,blank=True,null=True,related_name="from_artist",on_delete=models.DO_NOTHING)
    productivity_multiplier = models.FloatField(default=0.0,blank=False)
    productivity_type = models.CharField(max_length=10,blank=False,null=False)
    fk_task = models.ForeignKey('Tasks', blank=False, null=False, on_delete=models.CASCADE)
    int_app_date = models.DateField(null=True, blank=True)
    final_app_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


class Productivity(models.Model):
    fk_user = models.ForeignKey(User,null=False,blank=False,on_delete=models.CASCADE)
    productivity = models.FloatField(max_length=20,default=0.0)
    productivity_type = models.CharField(max_length=20,default='N/A')
    fk_assignment_log = models.ForeignKey("AssignmentLog",blank=True,null=True,on_delete=models.CASCADE)
    fk_task = models.ForeignKey('Tasks',null=True,blank=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)



class TruthTableForPost(models.Model):
    bg_status = models.CharField(max_length=20,default="N/A")
    ch_status = models.CharField(max_length=20,default="N/A")
    mg_status = models.CharField(max_length=20,default="N/A")
    fx_status = models.CharField(max_length=20,default="N/A")
    final_status = models.CharField(max_length=30)
    process = models.CharField(max_length=30,default="N/A")
    created_at = models.DateTimeField(default=timezone.now)


class RenderTask(models.Model):
    fk_task = models.ForeignKey("Tasks",null=False,blank=False,on_delete=models.CASCADE)
    is_fresh = models.BooleanField(default=True)
    is_current = models.BooleanField(default=True)  #for Notifying Lighting Artist About Current_Status
    assigned = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE)
    status = models.CharField(max_length=20,default='RTS')
    render_location = models.CharField(max_length=20, blank=True, null=True)
    frame_count = models.CharField(max_length=20,null=True,blank=True,default="0")
    render_path = models.TextField()
    render_done_time = models.DateTimeField(null=True,blank=True,default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)


class RenderLayer(models.Model):
    fk_render_task = models.ForeignKey("RenderTask",null=False,blank=False,on_delete=models.CASCADE)
    name = models.CharField(max_length=200,default="N/A")
    category = models.CharField(max_length=10)
    to_frame = models.CharField(max_length=10)
    from_frame = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    required_frame = models.CharField(max_length=50,null=True,blank=True)
    purpose_of_bounce = models.CharField(max_length=150)
    priority = models.CharField(max_length=10)
    path = models.TextField()
    job_id = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    render_time_per_frame_in_minute = models.CharField(max_length=5, default=0)

    
class RenderStatusLog(models.Model):
    fk_render_task = models.ForeignKey("RenderTask",null=False,blank=False,on_delete=models.CASCADE)
    to_status = models.CharField(max_length=20,blank=True,null=True,default="N/A")
    from_status = models.CharField(max_length=20,blank=True,null=True,default="N/A")
    created_by = models.ForeignKey(User, blank=True, null=True,on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now)


class ProjectConfiguration(models.Model):
    process = models.CharField(max_length=50,null=False,blank=False)
    project = models.CharField(max_length=20,null=False,blank=False)
    internal_authority = models.CharField(max_length=30,blank=False,null=False)
    internal_percent = models.CharField(max_length=10,blank=False,null=False)
    external_authority = models.CharField(max_length=30,blank=False,null=False)
    external_percent = models.CharField(max_length=10,blank=False,null=False)
    when_twenty_percent = models.CharField(max_length=20,blank=False,null=False,default="N/A")
    when_create_new_task = JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    
    
class ScanFile(models.Model):
    files = JSONField(null=True,default=dict)
    scan_id = models.CharField(max_length=30,null=True,blank=True)
    status = models.CharField(max_length=15,blank=True,null=True)
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)


class ShiftRooster(models.Model):
    jan_planned = JSONField(default=dict, blank=True, null=True)
    jan_actual = JSONField(default=dict, blank=True, null=True)
    jan_timestamp = JSONField(default=dict, blank=True, null=True)
    feb_planned = JSONField(default=dict, blank=True, null=True)
    feb_actual = JSONField(default=dict, blank=True, null=True)
    feb_timestamp = JSONField(default=dict, blank=True, null=True)
    mar_planned = JSONField(default=dict, blank=True, null=True)
    mar_actual = JSONField(default=dict, blank=True, null=True)
    mar_timestamp = JSONField(default=dict, blank=True, null=True)
    apr_planned = JSONField(default=dict, blank=True, null=True)
    apr_actual = JSONField(default=dict, blank=True, null=True)
    apr_timestamp = JSONField(default=dict, blank=True, null=True)
    may_planned = JSONField(default=dict, blank=True, null=True)
    may_actual = JSONField(default=dict, blank=True, null=True)
    may_timestamp = JSONField(default=dict, blank=True, null=True)
    jun_planned = JSONField(default=dict, blank=True, null=True)
    jun_actual = JSONField(default=dict, blank=True, null=True)
    jun_timestamp = JSONField(default=dict, blank=True, null=True)
    jul_planned = JSONField(default=dict, blank=True, null=True)
    jul_actual = JSONField(default=dict, blank=True, null=True)
    jul_timestamp = JSONField(default=dict, blank=True, null=True)
    aug_planned = JSONField(default=dict, blank=True, null=True)
    aug_actual = JSONField(default=dict, blank=True, null=True)
    aug_timestamp = JSONField(default=dict, blank=True, null=True)
    sep_planned = JSONField(default=dict, blank=True, null=True)
    sep_actual = JSONField(default=dict, blank=True, null=True)
    sep_timestamp = JSONField(default=dict, blank=True, null=True)
    oct_planned = JSONField(default=dict, blank=True, null=True)
    oct_actual = JSONField(default=dict, blank=True, null=True)
    oct_timestamp = JSONField(default=dict, blank=True, null=True)
    nov_planned = JSONField(default=dict, blank=True, null=True)
    nov_actual = JSONField(default=dict, blank=True, null=True)
    nov_timestamp = JSONField(default=dict, blank=True, null=True)
    dec_planned = JSONField(default=dict, blank=True, null=True)
    dec_actual = JSONField(default=dict, blank=True, null=True)
    dec_timestamp = JSONField(default=dict, blank=True, null=True)
    year = models.CharField(max_length=10,blank=True,null=True)
    fk_user = models.ForeignKey(User, related_name="shift_roster_user", blank=False, null=False,
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=10, choices=(
        ("DLF", "DLF"),
        ("KOLKATA", "KOLKATA")
    ))

class Notes(models.Model):
    note = models.TextField()
    fk_task = models.ForeignKey(Tasks,blank=True,null=True,on_delete=models.CASCADE)
    process = models.CharField(max_length=30,default='N/A')
    from_process = models.CharField(max_length=30, default='N/A')
    to_process = models.CharField(max_length=30, default='N/A')
    is_review_note = models.BooleanField(default=False)
    review_type = models.CharField(max_length=20,default='N/A')
    retake_type_tag = models.CharField(max_length=200, null=False, blank=False)
    created_for = models.ForeignKey(User,related_name="note_reader",null=True,blank=True,on_delete=DO_NOTHING)
    created_by = models.ForeignKey(User,related_name="note_creator",null=True,blank=True,on_delete=DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now)


class FileLog(models.Model):
    fk_task = models.ForeignKey(Tasks,null=False,blank=False,on_delete=models.CASCADE)
    fk_user = models.ForeignKey(User,related_name="user_submitted",on_delete=models.DO_NOTHING)
    versions = models.TextField()
    filename = JSONField()
    created_at = models.DateTimeField(default=timezone.now)


class PostStatus(models.Model):
    process = models.CharField(max_length=50,blank=False,null=False)
    bg_status = models.CharField(max_length=50,blank=False,null=False)
    ch_status = models.CharField(max_length=50,blank=False,null=False)
    final_status = models.CharField(max_length=50,blank=False,null=False)


class Scheduler(models.Model):
    project = models.CharField(max_length=50,blank=False,null=False)
    process = models.CharField(max_length=50,blank=False,null=False,default='N/A')
    fk_user = models.ForeignKey(User, null=False, blank=False, related_name="scheduler_user", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=2000,blank=False,null=False,default='N/A')
    episode = models.CharField(max_length=50,blank=False,null=False,default='N/A')
    prod_type = models.CharField(max_length=50,blank=False,null=False,default='N/A')
    version = models.CharField(max_length=50,blank=False,null=False,default='N/A')
    lock_status = models.BooleanField(default=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)



class ClientFeedbackAnalysis(models.Model):
    uploaded_by = models.ForeignKey(User,related_name='uploaded_by',blank=False,null=False,on_delete=DO_NOTHING)
    fk_project = models.ForeignKey(Projects, null=True, blank=True, on_delete=models.CASCADE)
    episode = models.CharField(max_length=500, blank=True, null=True)
    sequence = models.CharField(max_length=500, blank=True, null=True)
    shot = models.CharField(max_length=500, blank=True, null=True)
    stage = models.CharField(max_length=500, blank=True, null=True)
    take = models.IntegerField(blank=True, null=True)
    shot_status = models.CharField(max_length=500, blank=True, null=True)
    client_notes = models.TextField()
    cs_notes = models.TextField()
    cam_change = models.BooleanField(default=False)
    frame_change = models.BooleanField(default=False)
    asset_change = models.BooleanField(default=False)
    penetration = models.BooleanField(default=False)
    anim_change = models.BooleanField(default=False)
    lip_sync = models.BooleanField(default=False)
    facial = models.BooleanField(default=False)
    extra_pass = models.BooleanField(default=False)
    hair = models.BooleanField(default=False)
    fur = models.BooleanField(default=False)
    lighting = models.BooleanField(default=False)
    lighting_qc = models.BooleanField(default=False)
    comp = models.BooleanField(default=False)
    vfx = models.BooleanField(default=False)
    slide_or_float = models.BooleanField(default=False)
    tech = models.BooleanField(default=False)
    extra_pass = models.BooleanField(default=False)
    anim_mode = models.BooleanField(default=False)
    texture_retake = models.BooleanField(default=False)
    extra_retake = models.BooleanField(default=False)
    previous_note_not_followed = models.BooleanField(default=False)
    general = models.BooleanField(default=False)
    hookup = models.BooleanField(default=False)
    internal = models.BooleanField(default=False)
    client = models.BooleanField(default=False)
    misc = models.TextField()
    feedback_date = models.DateTimeField()
    feedback_id = models.CharField(max_length=500, blank=True, null=True)
    feedback_updated_by = ArrayField(models.TextField(),blank=True,null=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

''' TRACKER MODELS END'''
