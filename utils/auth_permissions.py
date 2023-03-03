from rest_framework import permissions
    
class IsPostOrGetOrIsAuthenticated(permissions.BasePermission):        
  def has_permission(self, request, view):
    if request.method == 'POST' or request.method == 'GET':
      return True
    
    return request.user and request.user.is_authenticated

class IsPostOrIsAuthenticated(permissions.BasePermission):        
  def has_permission(self, request, view):
    if request.method == 'POST':
      return True
    
    return request.user and request.user.is_authenticated

class IsGetOrIsAuthenticated(permissions.BasePermission):        
  def has_permission(self, request, view):
    if request.method == 'GET':
      return True
    
    return request.user and request.user.is_authenticated