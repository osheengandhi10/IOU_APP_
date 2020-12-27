from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import *
from rest_framework.views import APIView
from django.http import JsonResponse
import json
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseRedirect

class GetUser(APIView):

    def get(self,request):
        users = User.objects.all().values_list('username', flat=True) 
        users = list(users)
        user_dict = {}
        user_dict['users'] = users
        print(user_dict)
        context = json.dumps(user_dict)
        print(type(context))
        return render(request, "getusers.html", json.loads(context)) 
        
      

class CreateUSer(APIView):
    def post(self,request):
        print("enter create user")
        print(request.data)
        all_usernames = list(User.objects.values_list('username',flat = True))
        print(all_usernames)
        if request.data['username'] in all_usernames:
            return HttpResponse('Username already exists. Please try again with another username')
        else:
            User.objects.create(username = request.data['username'])

            return HttpResponse('User '+request.data['username']+ ' created successfully')



class CreateIOU(APIView):
    def post(self,request):
        print("********************************",request.data)
        data = request.data
        print("get or create user")
        create_lender = User.objects.get_or_create(username=data['lender'])
        create_borrower = User.objects.get_or_create(username=data['borrower'])
        print(create_lender,create_borrower)
        get_lender = User.objects.get(username=data['lender'])
        get_borrower = User.objects.get(username=data['borrower'])
        # lender json update
        if User_IOU.objects.filter(user=get_lender).exists():
          
            print("lender already exists IO need to update that")
            get_lender_IOU = User_IOU.objects.get(user = get_lender)
            lender_json = get_lender_IOU.IOU_json
            print(lender_json)
            if get_borrower.username in lender_json['owed_by']:
                print("enter alreadybexist")
                lender_json['owed_by'][get_borrower.username] += data['amount']
                print(lender_json)
            else:
                new_dict2 = {get_borrower.username :data['amount']}
                lender_json['owed_by'].update(new_dict2)
            print("lender json",lender_json)
            User_IOU.objects.filter(user=get_lender).update(IOU_json=lender_json)
            


        else:
           
            print(" lender Does not exist create new")
            IO_jsonfield_lender = User_IOU._meta.get_field('IOU_json')
            default_jsonIO_lender = IO_jsonfield_lender.default.copy()
            print("default",default_jsonIO_lender)
            default_jsonIO_lender['name'] = get_lender.username
            new_dict = {get_borrower.username :data['amount']}
            default_jsonIO_lender['owed_by'] = new_dict
            data_lender_db =  {'user': get_lender,'IOU_json': default_jsonIO_lender}
            User_IOU.objects.create(**data_lender_db)


        get_IO_lender = User_IOU.objects.get(user = get_lender)
        get_lender_final_json = get_IO_lender.IOU_json
        sum_ofowedby_lender =0
        sum_ofowes_lender = 0
        for i in get_lender_final_json['owed_by'].values():
            sum_ofowedby_lender = sum_ofowedby_lender +i
        print(sum_ofowedby_lender)
        for j in get_lender_final_json['owes'].values():
            sum_ofowes_lender = sum_ofowes_lender +j
        print(sum_ofowes_lender)
        balance_lender = sum_ofowedby_lender - sum_ofowes_lender
        get_IO_lender.IOU_json['balance'] = balance_lender
        get_IO_lender.save()
        # borrower json update
        if User_IOU.objects.filter(user= get_borrower).exists():
            print(" borrower already exists IO need to update that")

            get_borrower_IOU = User_IOU.objects.get(user = get_borrower)
            borrower_json = get_borrower_IOU.IOU_json
            print(borrower_json)
            if get_lender.username in borrower_json['owes']:
                print("enter alreadybexist")
                borrower_json['owes'][get_lender.username] += data['amount']
                print(borrower_json)
            else:
                new_dict3 = {get_lender.username :data['amount']}
                borrower_json['owes'].update(new_dict3)
            print(borrower_json)
            User_IOU.objects.filter(user=get_borrower).update(IOU_json=borrower_json)

        else:
            print(" borrower Does not exist create new")
           
            IO_jsonfield_borrower = User_IOU._meta.get_field('IOU_json')
            default_jsonIO_borrower = IO_jsonfield_borrower.default.copy()
            default_jsonIO_borrower['name'] = get_borrower.username
            new_dict1 = {get_lender.username : data['amount']}
            default_jsonIO_borrower['owes'].update(new_dict1)
            data_borrower_db =  {'user': get_borrower,'IOU_json': default_jsonIO_borrower}
            User_IOU.objects.create(**data_borrower_db)

        get_IO_borrower = User_IOU.objects.get(user = get_borrower)
        get_borrower_final_json = get_IO_borrower.IOU_json
        sum_ofowedby_borrower =0
        sum_ofowes_borrower = 0
        for i in get_borrower_final_json['owed_by'].values():
            sum_ofowedby_borrower = sum_ofowedby_borrower +i
        print(sum_ofowedby_borrower)
        for j in get_borrower_final_json['owes'].values():
            sum_ofowes_borrower = sum_ofowes_borrower +j
        print(sum_ofowes_borrower)
        balance_borrower = sum_ofowedby_borrower - sum_ofowes_borrower
        get_IO_borrower.IOU_json['balance'] = balance_borrower
        get_IO_borrower.save()
            
        
        print(get_IO_lender.id,get_IO_borrower.id)
        lender_id = get_IO_lender.id
        borrower_id = get_IO_borrower.id
        url_redirect = 'getsummary/<lender_id>/<borrower_id>/'
     
        return HttpResponseRedirect("getsummary/{lender_id}/{borrower_id}/".format(lender_id= lender_id,borrower_id= borrower_id))

class product_detail(APIView):
    def get(self,request,lender_id,borrower_id):
        print("enter summary",lender_id,borrower_id)
        context = {}
        user_lender = User_IOU.objects.get(id = lender_id).IOU_json
        user_borrower = User_IOU.objects.get(id = borrower_id).IOU_json
        context = {"lenderjson":json.dumps(user_lender),"borrowerjson":json.dumps(user_borrower)}
        return render(request,'showiou.html',context)



