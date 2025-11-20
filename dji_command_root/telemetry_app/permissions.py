from rest_framework import permissions

class IsSystemAdmin(permissions.BasePermission):
    """
    自定义权限：只允许系统管理员访问
    检查 UserProfile 中的 role 字段是否为 'admin'
    """

    def has_permission(self, request, view):
        # 首先必须是已登录用户
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 检查是否是超级管理员 (Django自带)
        if request.user.is_superuser:
            return True
            
        # 检查 UserProfile 中的 role
        # 注意：我们需要处理 UserProfile 不存在的情况
        try:
            return request.user.profile.role == 'admin'
        except AttributeError:
            # 如果没有 profile，默认没有权限 (除非是 superuser，上面已处理)
            return False
