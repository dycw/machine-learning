from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import Type
from typing import Union

from bokeh.document import Document
from bokeh.io import show
from bokeh.layouts import layout
from bokeh.models import Button
from bokeh.models import Slider
from holoviews import Curve
from holoviews import DynamicMap
from holoviews import renderer
from holoviews.streams import Stream
from numpy import linspace
from numpy import pi
from numpy import sin


@dataclass
class XData:
    title: str
    start: Union[int, float]
    stop: Union[int, float]
    step: Union[int, float]
    speed: int


_RENDERER = renderer("bokeh").instance(mode="server")


class Animation(ABC):
    _play_text = "► Play"
    _pause_text = "❚❚ Pause"

    def __init__(self: Animation) -> None:
        self._button = Button(label=self._play_text, width=60)
        xd = self._x_data
        self._slider = Slider(
            title=xd.title,
            start=xd.start,
            end=xd.stop,
            value=xd.start,
            step=xd.step,
        )
        self._slider.on_change("value", self._if_slider_updated)
        self._stream = Stream.define(xd.title, **{xd.title: xd.start})()
        self._dmap = DynamicMap(self._plot, streams=[self._stream])

    @classmethod
    def add_animation(cls: Type[Animation]) -> None:
        animation = cls()
        show(animation._modify_doc, notebook_url="localhost:8888")

    def _if_start_play(self: Animation) -> None:
        xd = self._x_data
        new_value = self._slider.value + xd.step
        if new_value > xd.stop:
            new_value = xd.start
        self._slider.value = new_value

    def _if_button_clicked(self: Animation, doc: Document) -> None:
        if self._button.label == self._play_text:
            self._button.label = self._pause_text
            self._callback_id = doc.add_periodic_callback(
                self._if_start_play,
                self._x_data.speed,
            )
        else:
            self._button.label = self._play_text
            doc.remove_periodic_callback(self._callback_id)

    def _if_slider_updated(
        self: Animation,
        attr: Any,
        old: Any,
        new: Union[int, float],
    ) -> None:
        self._stream.event(**{self._x_data.title: new})

    def _modify_doc(self: Animation, doc: Document) -> Document:
        self._button.on_click(partial(self._if_button_clicked, doc=doc))
        plot = layout(
            [
                [_RENDERER.get_plot(self._dmap, doc).state],
                [self._slider, self._button],
            ],
        )
        doc.add_root(plot)
        return doc

    @abstractmethod
    def _plot(self: Animation, **kwargs: Any) -> Any:
        raise NotImplementedError

    @property
    def _x_data(self: Animation) -> XData:
        raise NotImplementedError


class SineCurve(Animation):
    def _plot(self: SineCurve, phase: float) -> Curve:  # type: ignore
        xs = linspace(0, 4 * pi)
        ys = sin(xs + phase)
        return Curve((xs, ys)).opts(width=800)

    @property
    def _x_data(self: SineCurve) -> XData:
        return XData(
            title="phase",
            start=0.0,
            stop=4 * pi,
            step=0.01,
            speed=10,
        )
