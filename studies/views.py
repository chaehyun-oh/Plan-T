from django.shortcuts import render, redirect, get_object_or_404
from .models import Study
from .forms import StudyForm, StudyTodoForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages

# Create your views here.
def index(request):
    category = request.GET.get("category")
    if category is None:
        category_studies = Study.objects.all()
    else:
        category_studies = Study.objects.filter(category=category)
    # print(category)
    # print(type(category))
    # for i in category_studies:
    #     print(i.category)
    #     print(type(i.category))
    context = {"category_studies": category_studies}
    return render(request, "studies/test/index.html", context)


def create(request):
    if request.method == "POST":
        studyform = StudyForm(request.POST)
        if studyform.is_valid():
            form = studyform.save(commit=False)
            form.owner = request.user
            form.save()
            return redirect("studies:index")
    else:
        studyform = StudyForm()
    context = {"studyform": studyform}
    return render(request, "studies/test/create.html", context)


def create_todos(request, study_pk):
    if request.method == "POST":
        study = Study.objects.get(pk=study_pk)
        todoForm = StudyTodoForm(request.POST)
        if todoForm.is_valid() and study.owner == request.user:
            todo = todoForm.save(commit=False)
            # 스터디원 모두를 위해 생성
            users = study.participated
            for user in users:
                todo.user_id = user
                todo.save()
        return redirect("studies:index")  # redirect 위치 임시


def detail(request, study_pk):
    study = get_object_or_404(Study, pk=study_pk)
    user = request.user
    check = False
    print(len(study.participated.all()))
    if study in user.join_study.all():
        check = True
    context = {"study": study, "check": check, "study_todo_form": StudyTodoForm()}
    return render(request, "studies/test/detail.html", context)


def join(request, study_pk):
    study = get_object_or_404(Study, pk=study_pk)
    # 탈퇴
    if study.participated.filter(pk=request.user.pk).exists():
        study.participated.remove(request.user)
        is_participated = False
    # 가입신청 or 초대 수락
    else:
        study.participated.add(request.user)
        is_participated = True
    context = {
        "is_participated": is_participated,
        "studyCount": study.participated.count(),
    }
    return redirect("studies:detail", study_pk)


def accept(request, user_pk, study_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)
    study = get_object_or_404(Study, pk=study_pk)

    # 강퇴
    if user.join_study.filter(pk=study_pk).exists():
        user.join_study.remove(study)
        is_accepted = False
    # 수락 or 초대
    else:
        if study.max_people >= len(study.participated.all()):
            user.join_study.add(study)
            is_accepted = True
        else:
            messages.error(request, "최대 인원을 초과하였습니다.")
            return redirect("studies:detail", study_pk)
    context = {
        "is_accepted": is_accepted,
        "studyCount": user.join_study.count(),
    }
    return redirect("studies:detail", study_pk)


# # 검증하는 시스템 대략적으로 만들어 봄
# def test(request, user_pk, study_pk):
#     user = get_object_or_404(get_user_model(), pk=user_pk)
#     study = get_object_or_404(Study, pk=study_pk)
#     # 이 부분 되는지 테스트 필요
#     # 만약 study에서 user를 가입 허용목록에 있으면
#     if user in study.participated:
#         pass  # 환영합니다.
#     else:
#         return ()  # 들어가지 못하게
#     context = {}
#     return JsonResponse(context)
