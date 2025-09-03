from marshmallow import Schema, fields, validates, ValidationError

class OperationInputSchema(Schema):
    id = fields.String(required=True)
    asset_code = fields.String(required=True)
    operation_type = fields.String(required=True)
    quantity = fields.Integer(required=True)
    operation_date = fields.Date(required=True)

    @validates("operation_type")
    def validate_type(self, val):
        if val not in ("BUY", "SELL"):
            raise ValidationError("operation_type must be BUY or SELL")
        return val

    @validates("quantity")
    def validate_qty(self, val):
        if val <= 0:
            raise ValidationError("quantity must be > 0")
        return val

class ProcessOperationsSchema(Schema):
    fidc_id = fields.String(required=True)
    operations = fields.List(fields.Nested(OperationInputSchema), required=True)

class ExportSchema(Schema):
    fidc_id = fields.String(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
