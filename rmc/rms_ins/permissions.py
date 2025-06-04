from rest_framework import permissions
from rms_ins.exceptions import DataValidationException

# class IsAccountingMaster(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if request.method == "POST" and request.user.has_perm("rmc.add_grouping"):
#             return True
#         elif request.method == "PUT" and request.user.has_perm("rmc.edit_grouping"):
#             return True
#         elif request.method == "PATCH" and request.user.has_perm("rmc.delete_grouping"):
#             return True
#         elif request.method in permissions.SAFE_METHODS and request.user.has_perm("rmc.view_grouping"):#permissions.SAFE_METHODS
#             return True
#         else:
#             return False
#             print(request.user,"request.user")
#             print(request.user.has_perm("rmc.add_grouping"),"request.user.has_perm(rmc.add_group)")
#             print(request.user.has_perm("rmc.edit_grouping"),"request.user.has_perm(rmc.change_group)")
#             print(request.user.has_perm("rmc.delete_grouping"),"request.user.has_perm(rmc.delete_group)")
#             print(request.user.has_perm("rmc.view_grouping"),"request.user.has_perm(rmc.view_group)")

class IsRmcAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # return request.user.has_perm("rmc.is_rmc_admin")
        if request.user.has_perm("rmc.is_rmc_admin"):
            return True
        else:
            raise DataValidationException(detail='You do not have permission to perform this action.',code = 403)

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # return request.user.is_superuser
        if request.user.is_superuser:
            return True
        else:
            raise DataValidationException(detail='You do not have permission to perform this action.Only Superuser can access.',code = 403)

class CheckPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Get a mapping of methods -> required_perms_mapping
        required_perms_mapping = getattr(view, "required_perms", {})
        # Determine the required perms for this particular request method.
        required_perms = required_perms_mapping.get(request.method,[])
        for perm in required_perms:
            # print(perm,"permission")
            # print(request.user.has_perm(perm),"request.user.has_perm(perm)")
            if request.user.has_perm(perm):
                return True
            else:
                print("false")
                raise DataValidationException(detail='You do not have permission to perform this action.',code = 403)
       
def HasUserPermission(request,required_perms):
    # print(required_perms,"required_perms")
    for perm in required_perms:
        if request.user.has_perm(perm):
            return True
        else:
            return False



    

    











