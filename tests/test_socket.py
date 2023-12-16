"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 16/12/2023
@Description  :
"""
import asyncio

import pytest
import websockets

from src.app.common.client.web_socket import WebSocketClient


def test_WebSocketClient():
    client = WebSocketClient("test")
    client.start_ws()
    client.send("Hello, WebSocket!")
    data = client.receive()
    assert data == "Message text was: Hello, WebSocket!"


@pytest.mark.asyncio
async def test_websocket():

    async with websockets.connect('ws://127.0.0.1:5000/ws/test') as websocket:

        await websocket.send("Hello, WebSocket!")
        data = await websocket.recv()
        assert data == "Message text was: Hello, WebSocket!"


@pytest.mark.asyncio
async def test_websocket_manager():

    async with websockets.connect('ws://127.0.0.1:5000/identify/test/ws/test_id') as websocket:

        await websocket.send("Hello, WebSocket!")
        data = await websocket.recv()
        assert data == "Hello, WebSocket!"

if __name__ == "__main__":
    asyncio.run(test_websocket())
