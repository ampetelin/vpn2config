import base64
import json
import zlib

from pydantic import BaseModel, Field, field_validator

from services.awg_converter.exceptions import DecodeError
from services.awg_converter.templates import AWG_TEMPLATE


class MagicJunk(BaseModel):
    H1: int
    H2: int
    H3: int
    H4: int
    Jc: int
    Jmin: int
    Jmax: int
    S1: int
    S2: int


class LastConfig(MagicJunk, BaseModel):
    client_id: str = Field(..., alias="clientId")
    client_private_key: str = Field(..., alias="client_priv_key")
    client_public_key: str = Field(..., alias="client_pub_key")
    client_ip: str
    MTU: int = Field(..., alias="mtu")
    server_public_key: str = Field(..., alias="server_pub_key")
    preshared_key: str = Field(..., alias="psk_key")
    hostname: str = Field(..., alias="hostName")
    port: int
    allowed_ips: list[str]
    persistent_keepalive: int = Field(..., alias="persistent_keep_alive")
    config: str


class AWG(MagicJunk, BaseModel):
    last_config: LastConfig
    port: int
    transport_proto: str

    @field_validator("last_config", mode="before")
    @classmethod
    def parse_last_config(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class Container(BaseModel):
    awg: AWG
    container: str


class Config(BaseModel):
    containers: list[Container]
    default_container: str = Field(..., alias="defaultContainer")
    description: str
    dns1: str
    dns2: str
    hostname: str = Field(..., alias="hostName")

    def get_raw_config(self) -> str:
        default_container = next(
            container for container in self.containers if container.container == self.default_container
        )
        config = default_container.awg.last_config

        return AWG_TEMPLATE.substitute(
            address=config.client_ip,
            DNS=', '.join([self.dns1, self.dns2]),
            DNS1=self.dns1,
            DNS2=self.dns2,
            private_key=config.client_private_key,
            MTU=config.MTU,
            H1=config.H1,
            H2=config.H2,
            H3=config.H3,
            H4=config.H4,
            Jc=config.Jc,
            Jmin=config.Jmin,
            Jmax=config.Jmax,
            S1=config.S1,
            S2=config.S2,
            public_key=config.server_public_key,
            preshared_key=config.preshared_key,
            allowed_ips=', '.join(config.allowed_ips),
            endpoint_address=config.hostname,
            endpoint_port=config.port,
            persistent_keepalive=config.persistent_keepalive,
        )


def decode_config(encoded_string: str):
    encoded_data = encoded_string.replace("vpn://", "")

    try:
        padding = 4 - (len(encoded_data) % 4)
        encoded_data += "=" * padding
        compressed_data = base64.urlsafe_b64decode(encoded_data)

        original_data_len = int.from_bytes(compressed_data[:4], byteorder='big')
        decompressed_data = zlib.decompress(compressed_data[4:])

        if len(decompressed_data) != original_data_len:
            raise DecodeError("Invalid length of decompressed data")
        return Config.model_validate_json(decompressed_data)
    except Exception as ex:
        raise DecodeError("Couldn't decrypt the link", ex)
