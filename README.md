# Aero Hand Open SDK

基于 [Chestnut Robotics 的 Aero Hand Open](https://github.com/Chestnut-Robotics/aero-hand-open) 改造的 Python 上位机项目，包含串口控制 SDK、中文 GUI 和示例。上游版权及许可见 [NOTICE](NOTICE) 和 [LICENSE](LICENSE)。

## 环境要求

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.10 或更新版本（仓库的 `.python-version` 指定 3.10，uv 可自动准备）
- GUI 运行环境需要 Tkinter 和图形桌面；串口控制需要已连接的 Aero Hand 设备

## 安装与运行

克隆本仓库并进入项目目录后执行：

```bash
uv sync
uv run aero-open-gui
```

`uv sync` 会按 `pyproject.toml` 和提交的 `uv.lock` 创建 `.venv` 并安装项目及依赖。需要严格复现锁文件时使用 `uv sync --locked`。更新依赖后运行 `uv lock`，并提交新的 `uv.lock`。

在本工作区中也可以执行上级目录的 `./host.sh` 启动 GUI。该脚本不属于本仓库；单独克隆时请用上面的 `uv run aero-open-gui`。

GUI 使用 Python 自带的 Tkinter。若出现 `No module named tkinter`，请给实际使用的 Python 安装对应的 Tk/Tcl 支持；在 Debian/Ubuntu 使用系统 Python 时通常需要 `python3-tk`。Tkinter 无法通过 `uv sync` 作为 PyPI 包安装。

## 串口连接

GUI 内刷新并选择设备串口。Linux 常见设备名为 `/dev/ttyACM0` 或 `/dev/ttyUSB0`，可用 `ls -l /dev/serial/by-id/` 查找稳定路径。SDK 的 `AeroHand()` 在 Linux 上会尝试自动检测 Espressif USB JTAG 串口；也可以显式指定端口：

```python
from aero_open_sdk.aero_hand import AeroHand

hand = AeroHand(port="/dev/ttyACM0")
try:
    print(hand.get_actuations())
finally:
    hand.close()
```

Windows 请传入对应的 `COM` 端口。Linux 如遇串口权限错误，请检查设备所属用户组，必要时将当前用户加入 `dialout` 并重新登录。

GUI 的“烧录固件”功能依赖随项目安装的 `esptool`。操作前请确认所选 `.bin` 文件和烧录地址适合目标 ESP32；固件源码及构建流程不在此 SDK 仓库中。

## 示例

`examples/` 包含回零、关节控制、舵机微调和状态读取等示例。它们会访问真实设备，运行前先确认串口和机械运动范围。例如：

```bash
uv run python examples/get_info.py
```

键盘控制示例额外使用 `pynput`：

```bash
uv sync --extra examples
uv run --extra examples python examples/power_grasp.py
```

## 构建与发布

```bash
uv sync --locked
uv build
```

构建产物位于 `dist/`，已被 Git 忽略。向 GitHub 发布源码时提交 `pyproject.toml`、`uv.lock`、`src/`、`examples/`、README、LICENSE 和 NOTICE；不要提交 `.venv/` 或 `dist/`。`其他文件/` 保存了原有的模型和硬件参考文件，不会进入 Python wheel。该目录中两份 STEP 模型各约 53 MiB，推送到 GitHub 时会收到大文件警告；若计划长期维护这些模型，可考虑 Git LFS。

本仓库使用 [Apache License 2.0](LICENSE)。项目与上游的关系及原始版权声明见 [NOTICE](NOTICE)。
