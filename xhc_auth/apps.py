from django.apps import AppConfig


class XhcAuthConfig(AppConfig):
    # 指定该应用中所有模型的默认主键字段类型，BigAutoField是Django中的一种自动递增的整数字段类型，使用 64 位整数作为主键（支持更大的数值范围）
    default_auto_field = 'django.db.models.BigAutoField'
    # 指定应用的名称，Django会根据这个名称自动获取应用的其他信息
    name = 'xhc_auth'
