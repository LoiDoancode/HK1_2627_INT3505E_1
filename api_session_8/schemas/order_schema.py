try:
    from marshmallow import Schema, fields, validate, validates, ValidationError
    HAS_MARSHMALLOW = True
except ImportError:
    HAS_MARSHMALLOW = False

if HAS_MARSHMALLOW:
    class OrderItemIn(Schema):
        product_id = fields.Int(required=True)
        quantity = fields.Int(
            required=True,
            validate=validate.Range(min=1, error="Số lượng sản phẩm trong đơn hàng phải >= 1"),
        )

    class OrderIn(Schema):
        customer_name = fields.Str(
            required=True,
            validate=validate.Length(min=1, max=255),
        )
        customer_email = fields.Email(allow_none=True, load_default=None)
        items = fields.List(
            fields.Nested(OrderItemIn),
            required=True,
            validate=validate.Length(min=1, error="Đơn hàng phải chứa ít nhất 1 sản phẩm"),
        )

        @validates("customer_name")
        def validate_customer_name(self, value, **kwargs):
            if not value or value.strip() == "":
                raise ValidationError("Tên khách hàng không được để trống")

    class OrderItemOut(Schema):
        id = fields.Int()
        order_id = fields.Int()
        product_id = fields.Int()
        quantity = fields.Int()
        unit_price_cents = fields.Int()
        subtotal_cents = fields.Int()
        product = fields.Dict(allow_none=True)

    class OrderOut(Schema):
        id = fields.Int()
        customer_name = fields.Str()
        customer_email = fields.Str(allow_none=True)
        status = fields.Str()
        total_amount_cents = fields.Int()
        created_at = fields.DateTime(dump_only=True)
        items = fields.List(fields.Nested(OrderItemOut))

else:
    try:
        from ..errors import ValidationError
    except (ImportError, ValueError):
        from errors import ValidationError

    class OrderItemIn:
        def load(self, data):
            if not isinstance(data, dict):
                raise ValidationError("Mỗi item phải là 1 JSON object")
            pid = data.get("product_id")
            qty = data.get("quantity")
            if not isinstance(pid, int):
                raise ValidationError("product_id phải là số nguyên")
            if not isinstance(qty, int) or qty < 1:
                raise ValidationError("quantity phải là số nguyên >= 1")
            return {"product_id": pid, "quantity": qty}

    class OrderIn:
        def load(self, data):
            if not isinstance(data, dict):
                raise ValidationError("Payload phải là JSON object")
            name = data.get("customer_name")
            email = data.get("customer_email")
            items = data.get("items")

            if not name or not isinstance(name, str) or name.strip() == "" or len(name) > 255:
                raise ValidationError("customer_name không hợp lệ (1-255 ký tự)")
            if not items or not isinstance(items, list) or len(items) == 0:
                raise ValidationError("Đơn hàng phải chứa ít nhất 1 sản phẩm trong 'items'")

            parsed_items = [OrderItemIn().load(i) for i in items]
            return {
                "customer_name": name.strip(),
                "customer_email": email,
                "items": parsed_items,
            }

    class OrderOut:
        def dump(self, obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            return obj
