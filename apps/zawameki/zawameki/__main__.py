"""python -m zawameki で起動する。"""
from __future__ import annotations

import os

import uvicorn


def main() -> None:
    kwargs = {}
    # 別ポートで直接 HTTPS を出すとき（前段に nginx 等を置かない場合）
    if os.environ.get("ZAWAMEKI_SSL_CERTFILE") and os.environ.get("ZAWAMEKI_SSL_KEYFILE"):
        kwargs["ssl_certfile"] = os.environ["ZAWAMEKI_SSL_CERTFILE"]
        kwargs["ssl_keyfile"] = os.environ["ZAWAMEKI_SSL_KEYFILE"]
    uvicorn.run(
        "zawameki.app:create_app", factory=True,
        host=os.environ.get("ZAWAMEKI_HOST", "0.0.0.0"),
        port=int(os.environ.get("ZAWAMEKI_PORT", "8100")),
        proxy_headers=True, forwarded_allow_ips=os.environ.get("ZAWAMEKI_TRUSTED_PROXIES", "127.0.0.1"),
        ws_ping_interval=20, ws_ping_timeout=20,
        # 状態は1プロセスのメモリに持つので、ワーカーは1つに限る
        workers=1, log_level=os.environ.get("ZAWAMEKI_LOG_LEVEL", "info"),
        **kwargs,
    )


if __name__ == "__main__":
    main()
