# from django.db.models.fields.files import FieldFile, ImageField
#
# from ..consts import *
#
#
# def parse_obj_to_pdf_builder_data(obj, exclude_fields=None):
#     if exclude_fields is None:
#         exclude_fields = []
#     data = []
#     ctr = 0
#     for field in obj._meta.fields:
#         ctr += 1
#         if ctr == 3:
#             data.append({
#                 ROW_CONTENT: [
#                     {COL_SPACER: (25, 50)}
#                 ]
#             })
#         elif field.name not in exclude_fields:
#             is_image = False
#             field_value = getattr(obj, field.name)
#             if isinstance(field_value, FieldFile) or isinstance(field_value, ImageField):
#                 field_value = getattr(field_value, 'path') if field_value else None
#                 is_image = True
#             col1 = {
#                 COL_CONTENT: field.verbose_name,
#                 COL_ALIGN: COL_ALIGN_LEFT
#             }
#             col2 = {
#                 COL_CONTENT: field_value,
#                 COL_ALIGN: COL_ALIGN_CENTER
#             }
#             if is_image:
#                 col2.update({
#                     IMG_SIZE: {'width': 50, 'height': 50}
#                 })
#             columns = [col1, col2]
#             data.append({ROW_CONTENT: columns})
#     # print(data)
#     return data
