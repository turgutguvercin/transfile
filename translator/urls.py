"""
URL configuration for translator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('pikachu/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/', include("accounts.urls")),
    path('accounts/settings', auth_views.PasswordChangeView.as_view(
        template_name="settings/settings.html",
        success_url=reverse_lazy('account_settings_done')
    ), name="account_settings"),
    path('accounts/settings/done', auth_views.PasswordChangeDoneView.as_view(template_name="settings/settings_done.html"), name="account_settings_done"),
    path('', include("translate.urls")),
    path('', include("documents.urls")),
    path('blog/', include("blog.urls")),
    
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
