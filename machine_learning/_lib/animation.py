from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from contextlib import suppress
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
class _Description:
    title: str
    start: Union[int, float]
    stop: Union[int, float]
    step: Union[int, float]
    speed: int
    frame_width: int = 800
    frame_height: int = 400


_RENDERER = renderer("bokeh").instance(mode="server")


class Animation(ABC):
    _play_text = "► Play"

    def __init__(self: Animation) -> None:
        desc = self._description
        self._button = Button(label=self._play_text, width=60)
        self._is_playing_value = False
        self._slider = Slider(
            title=desc.title,
            start=desc.start,
            end=desc.stop,
            value=desc.start,
            step=desc.step,
        )
        self._slider.on_change("value", self._update_slider)
        self._stream = Stream.define(desc.title, **{desc.title: desc.start})()
        self._dmap = DynamicMap(self._plot_with_sizing, streams=[self._stream])

    @classmethod
    def add_animation(cls: Type[Animation]) -> None:
        animation = cls()
        show(animation._modify_doc, notebook_url="localhost:8888")

    def _continue_playing(self: Animation, doc: Document) -> None:
        desc = self._description
        new = self._slider.value + desc.step
        if new <= desc.stop:
            self._slider.value = new
        if new >= desc.stop:
            self._stop_playback(doc)

    @property
    def _description(self: Animation) -> _Description:
        raise NotImplementedError

    @property
    def _is_playing(self: Animation) -> bool:
        return self._is_playing_value

    @_is_playing.setter
    def _is_playing(self: Animation, is_playing: bool) -> None:
        if is_playing:
            self._button.label = "❚❚ Pause"
        else:
            self._button.label = self._play_text
        self._is_playing_value = is_playing

    def _modify_doc(self: Animation, doc: Document) -> Document:
        self._button.on_click(partial(self._toggle_playback, doc=doc))
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

    def _plot_with_sizing(self: Animation, **kwargs: Any) -> Any:
        desc = self._description
        return self._plot(**kwargs).opts(
            frame_width=desc.frame_width,
            frame_height=desc.frame_height,
        )

    def _start_playback(self: Animation, doc: Document) -> None:
        desc = self._description
        self._is_playing = True
        if self._slider.value >= desc.stop:
            self._slider.value = desc.start
        self._callback_id = doc.add_periodic_callback(
            partial(self._continue_playing, doc=doc),
            desc.speed,
        )

    def _stop_playback(self: Animation, doc: Document) -> None:
        self._is_playing = False
        with suppress(ValueError):
            doc.remove_periodic_callback(self._callback_id)

    def _toggle_playback(self: Animation, doc: Document) -> None:
        if self._is_playing:
            self._stop_playback(doc)
        else:
            self._start_playback(doc)

    def _update_slider(
        self: Animation,
        attr: Any,
        old: Any,
        new: Union[int, float],
    ) -> None:
        self._stream.event(**{self._description.title: new})


class SineCurve(Animation):
    @property
    def _description(self: SineCurve) -> _Description:
        return _Description(
            title="phase",
            start=0.0,
            stop=4 * pi,
            step=0.1 * pi,
            speed=100,
            frame_width=400,
            frame_height=400,
        )

    def _plot(self: SineCurve, phase: float) -> Curve:  # type: ignore
        xs = linspace(0, 4 * pi)
        ys = sin(xs + phase)
        return Curve((xs, ys))
