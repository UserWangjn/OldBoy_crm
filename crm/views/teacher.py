from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from crm import forms, models
from utils.pagination import Pagination
from django.urls import reverse
from django.views import View
from django.db.models import Q
import copy
from django.http import QueryDict
from django.utils.safestring import mark_safe
from django.db import transaction


# 班级展示列表
class ClassList(View):
    def get(self, request):
        # 模糊搜索
        q = self.get_search_contion(['course', 'semester'])
        all_class = models.ClassList.objects.filter(q)
        query_params = self.get_next_url()
        page = Pagination(request, all_class.count(), request.GET.copy())
        return render(request, 'crm/teacher/class_list.html',
                      {'all_class': all_class[page.start:page.end], 'query_params': query_params})

    def get_next_url(self):
        next = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = next
        next_url = qd.urlencode()

        return next_url

    def get_search_contion(self, query_list):
        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q


# 添加、编辑班级
def classes(request, edit_id=None):
    obj = models.ClassList.objects.filter(id=edit_id).first()
    # print(obj)
    form_obj = forms.ClassForm(instance=obj)
    tittle = '编辑班级列表' if obj else '新增班级列表'
    if request.method == 'POST':
        form_obj = forms.ClassForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('class_list'))
    return render(request, 'crm/base_form.html', {'form_obj': form_obj, 'tittle': tittle})


# 展示课程列表
class CourseList(View):
    def get(self, request, class_id):
        # 模糊搜索
        q = self.get_search_contion([])
        all_course = models.CourseRecord.objects.filter(q, re_class_id=class_id)
        query_params = self.get_next_url()
        page = Pagination(request, all_course.count(), request.GET.copy())
        return render(request, 'crm/teacher/course_list.html',
                      {'all_course': all_course[page.start:page.end], 'query_params': query_params,
                       'class_id': class_id})

    def post(self, request, class_id):
        # print(request.POST)   # <QueryDict: {'csrfmiddlewaretoken': ['KOIBZh8aVJ7xQM7ZxwgZfK4Wd3atAa1BdbxJJyx4x3g4W7eJfS5MkppIvuwGRFMC'], 'action': ['multi_to_pri'], 'id': ['2', '3', '6']}>
        action = request.POST.get('action')
        if not hasattr(self, action):
            return HttpResponse('不存在的操作')
        ret = getattr(self, action)()
        if ret:
            return ret
        # return redirect(reverse('customer'))
        return self.get(request, class_id)

    def get_next_url(self):
        next = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = next
        next_url = qd.urlencode()

        return next_url

    def get_search_contion(self, query_list):
        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q

    def multi_init(self):
        course_ids = self.request.POST.getlist('id')
        course_obj_list = models.CourseRecord.objects.filter(id__in=course_ids)
        for course_obj in course_obj_list:
            all_students = course_obj.re_class.customer_set.filter(status='studying')
            student_list = []
            for student in all_students:
                # 方式一
                # models.StudyRecord.objects.create(course_record=course_obj,student=student)
                # 方式二
                student_list.append(models.StudyRecord(course_record=course_obj, student=student))
            models.StudyRecord.objects.bulk_create(student_list)


# 新增和编辑课程
def course(request, class_id=None, edit_id=None):
    obj = models.CourseRecord.objects.filter(id=edit_id).first() or models.CourseRecord(re_class_id=class_id,
                                                                                        teacher=request.user)
    # print(obj)
    form_obj = forms.CourseForm(instance=obj)
    tittle = '编辑课程列表' if edit_id else '新增课程列表'
    if request.method == 'POST':
        form_obj = forms.CourseForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('course_list', args=(class_id,)))
    return render(request, 'crm/base_form.html', {'form_obj': form_obj, 'tittle': tittle})


from django.forms import modelformset_factory


def study_record(request, course_id):
    FormSet = modelformset_factory(models.StudyRecord, forms.StudyRecordForm,extra=0)
    queryset = models.StudyRecord.objects.filter(course_record_id=course_id)
    form_set = FormSet(queryset=queryset)
    if request.method == 'POST':
        form_set = FormSet(request.POST)
        if form_set.is_valid():
            form_set.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('study_record_list', args=(course_id,)))
    return render(request, 'crm/teacher/study_record_list.html',{'form_set':form_set})
