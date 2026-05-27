def user_name(request):
    return {"username": request.session.get("name")}