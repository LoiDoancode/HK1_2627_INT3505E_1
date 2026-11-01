try:
    from marshmallow import Schema, fields, validate, validates, ValidationError
    HAS_MARSHMALLOW = True
except ImportError:
    HAS_MARSHMALLOW = False

if HAS_MARSHMALLOW:
    # ─── OUTPUT SCHEMA ───
    class ProductOut(Schema):
        id = fields.Int()
        sku = fields.Str()
        name = fields.Str()
        description = fields.Str(allow_none=True)
        price_cents = fields.Int()
        qty_in_stock = fields.Int()
        archived = fields.Bool()
        created_at = fields.DateTime(dump_only=True)
        updated_at = fields.DateTime(dump_only=True)

    # ─── INPUT TẠO MỚI (Slide 24 & 30) ───
    class ProductIn(Schema):
        sku = fields.Str(
            required=True,
            validate=[
                validate.Length(min=3, max=32),
                validate.Regexp(r"^[A-Z0-9-]+$", error="SKU chỉ được chứa chữ hoa in, số và dấu gạch ngang"),
            ],
        )
        name = fields.Str(
            required=True,
            validate=validate.Length(min=1, max=255),
        )
        description = fields.Str(allow_none=True, load_default=None)
        price_cents = fields.Int(
            required=True,
            validate=validate.Range(min=0, error="Giá price_cents phải lớn hơn hoặc bằng 0"),
        )
        qty_in_stock = fields.Int(
            load_default=0,
            validate=validate.Range(min=0, error="Số lượng tồn kho phải >= 0"),
        )

        @validates("name")
        def validate_name(self, value, **kwargs):
            if not value or value.strip() == "":
                raise ValidationError("Tên sản phẩm không được để trống")

    # ─── INPUT CẬP NHẬT PARTIAL ───
    class ProductPatch(Schema):
        name = fields.Str(validate=validate.Length(min=1, max=255))
        description = fields.Str(allow_none=True)
        price_cents = fields.Int(validate=validate.Range(min=0))
        qty_in_stock = fields.Int(validate=validate.Range(min=0))

        @validates("name")
        def validate_name(self, value, **kwargs):
            if value is not None and value.strip() == "":
                raise ValidationError("Tên sản phẩm không được để trống")

    # ─── /RESERVE SCHEMA ───
    class ReserveIn(Schema):
        qty = fields.Int(
            required=True,
            validate=validate.Range(min=1, error="Số lượng reserve phải >= 1"),
        )

else:
    # Fallback thuần Python khi chưa chạy pip install marshmallow
    import re
    try:
        from ..errors import ValidationError
    except (ImportError, ValueError):
        from errors import ValidationError

    class ProductOut:
        def dump(self, obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            return obj

    class ProductIn:
        def load(self, data):
            if not isinstance(data, dict):
                raise ValidationError("Payload phải là một JSON object")
            
            sku = data.get("sku")
            name = data.get("name")
            price_cents = data.get("price_cents")
            qty_in_stock = data.get("qty_in_stock", 0)
            description = data.get("description")

            if not sku or not isinstance(sku, str) or not (3 <= len(sku) <= 32) or not re.match(r"^[A-Z0-9-]+$", sku):
                raise ValidationError("SKU không hợp lệ (độ dài 3-32 ký tự, chỉ gồm A-Z, 0-9, -)")
            if not name or not isinstance(name, str) or name.strip() == "" or len(name) > 255:
                raise ValidationError("Tên sản phẩm không hợp lệ (1-255 ký tự, không được rỗng)")
            if price_cents is None or not isinstance(price_cents, int) or price_cents < 0:
                raise ValidationError("price_cents phải là số nguyên >= 0")
            if not isinstance(qty_in_stock, int) or qty_in_stock < 0:
                raise ValidationError("qty_in_stock phải là số nguyên >= 0")

            return {
                "sku": sku,
                "name": name.strip(),
                "price_cents": price_cents,
                "qty_in_stock": qty_in_stock,
                "description": description,
            }

    class ProductPatch:
        def load(self, data, partial=True):
            if not isinstance(data, dict):
                raise ValidationError("Payload phải là JSON object")
            res = {}
            if "name" in data:
                name = data["name"]
                if not isinstance(name, str) or name.strip() == "" or len(name) > 255:
                    raise ValidationError("name không hợp lệ")
                res["name"] = name.strip()
            if "price_cents" in data:
                price = data["price_cents"]
                if not isinstance(price, int) or price < 0:
                    raise ValidationError("price_cents phải là số nguyên >= 0")
                res["price_cents"] = price
            if "qty_in_stock" in data:
                qty = data["qty_in_stock"]
                if not isinstance(qty, int) or qty < 0:
                    raise ValidationError("qty_in_stock phải là số nguyên >= 0")
                res["qty_in_stock"] = qty
            if "description" in data:
                res["description"] = data["description"]
            return res

    class ReserveIn:
        def load(self, data):
            if not isinstance(data, dict) or "qty" not in data:
                raise ValidationError("Payload phải chứa trường 'qty'")
            qty = data["qty"]
            if not isinstance(qty, int) or qty < 1:
                raise ValidationError("qty phải là số nguyên >= 1")
            return {"qty": qty}
