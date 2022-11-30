from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model as User
from .forms import TodosForm, TimetableForm
from .models import Timetable, Todos
from datetime import datetime


# Create your views here.
def today(request):
    user_pk = request.user.pk
    today = str(datetime.now())[:10]

    user_todos = Todos.objects.filter(user_id=user_pk)
    # started_at__lte=today, expired_at__gte=today
    # filter 에 추가할 조건
    # started 보다 today가 많고, expired 보다 today가 적다는 조건
    timetables = Timetable.objects.filter(today__startswith=today)
    # todo_id=user_todos
    # filter에 추가해야하는데 역참조 조건 달기가 까다로움
    # todo_id는 todo에 달린 user_id 가 request.user의 pk 이다
    # 아니면 todo_id는 user_todos 의 pk와 같다 라고 하면 되는데
    # 구현이 잘 안 됨

    todosForm = TodosForm()
    timetableForm = TimetableForm()

    context = {
        "todosForm": todosForm,
        "timetableForm": timetableForm,
        "user_todos": user_todos,
        "timetables": timetables,
    }
    return render(request, "todos/complete/today_main.html", context)


def create(request):
    user = request.user
    if request.method == "POST":
        todoForm = TodosForm(request.POST, request.FILES)
        if todoForm.is_valid():
            todo = todoForm.save(commit=False)
            todo.user_id = user
            todo.save()
    return redirect("todos:today")  # 추후에 비동기로 반드시 바꾸어 줘야 함.


def timetable(request):
    if request.method == "POST":
        timetable_form = TimetableForm(request.POST)
        if timetable_form.is_valid():
            timetable_form.save()
    return redirect("todos:today")


def delete(request, todos_pk):
    if request.method == "POST":
        todo = Todos.objects.get(pk=todos_pk)
        todo.delete()
    return redirect("todos:today")  # 추후에 비동기로 바꾸는거 권장


def week(request):
    # 미완성
    # 1
    # 날짜를 어떻게 받을지 아직 못정함.
    # 화면에 할일을 클릭은 주소 url이 좋을거 같지만
    # 여기서 값을 받는것은 JS를 활용한 input값 받기 일거 같다.
    # sunday_todos = Todos.objects.filter(started_at="일")
    # monday_todos = Todos.objects.filter(started_at="월")
    # tuesday_todos = Todos.objects.filter(started_at="화")
    # wednesday_todos = Todos.objects.filter(started_at="수")
    # thursday_todos = Todos.objects.filter(started_at="목")
    # friday_todos = Todos.objects.filter(started_at="금")
    # saturday_todos = Todos.objects.filter(started_at="토")
    # 다음주 지난주 클릭은 비동기로 axios를 사용하여 서버와 통신하게 만들어야 될 거 같다.

    # 2
    # 과거인지 지금 혹은 미래인지 구분하기
    # 장고에서 날짜 비교가 되는지 모르겠다.
    # 비교가 된다면
    # if 2022-11-29 <= 2022-12-01:
    #   a = True
    # else:
    #   a = False
    # 해서 7개의 변수를 만들어서 context로 보내준다.

    # 3
    todos = TodosForm()
    context = {
        "todos": todos,
    }
    return render(request, "todos/working/week_todos.html", context)


def read_all(request):
    todos = Todos.objects.filter(user_id=request.user)
    # 알고리즘 잘 작동하나 확인 필요
    # 예상 모형 [[2022-10-12,2022-10-12,2022-10-12],[2022-10-13,2022-10-13,2022-10-13],[2022-10-14,2022-10-14,2022-10-14]]
    time = ""
    all_days = []
    for todo in todos:
        if time != todo.started_at:
            time = todo.started_at
            all_days.append()
            all_days[-1].append(time)
        else:
            all_days[-1].append(time)
    context = {
        "all_days": all_days,
    }
    return render(request, "todos/working/read_all.html", context)
