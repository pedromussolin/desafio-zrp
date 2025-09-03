from marshmallow import Schema, fields, validate

class OperationSchema(Schema):
    asset_code = fields.String(required=True, validate=validate.Length(min=1))
    operation_type = fields.String(required=True, validate=validate.OneOf(["BUY", "SELL"]))
    quantity = fields.Float(required=True, validate=validate.Range(min=0))
    execution_price = fields.Float(required=True, validate=validate.Range(min=0))
    
class JobSchema(Schema):
    job_id = fields.String(required=True)
    status = fields.String(required=True, validate=validate.OneOf(["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"]))
    
class ExportSchema(Schema):
    format = fields.String(required=True, validate=validate.OneOf(["CSV", "JSON"]))
    destination = fields.String(required=True, validate=validate.Length(min=1))