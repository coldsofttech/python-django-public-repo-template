from example_project.urls import build_urlpatterns

urlpatterns = build_urlpatterns(api=False, ui=False, admin_site=False, docs=False)
