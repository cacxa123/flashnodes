from pydantic import BaseModel, constr


class Cryptocurrency(BaseModel):
    full_name: constr(min_length=1, max_length=64)
    symbol: constr(min_length=1, max_length=12, to_upper=True)
    details: constr(min_length=1)


class CryptocurrencyDB(BaseModel):
    id: int
    full_name: constr(min_length=1, max_length=64)
    symbol: constr(min_length=1, max_length=12, to_upper=True)
    details: constr(min_length=1)
