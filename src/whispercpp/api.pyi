from __future__ import annotations

import enum
import typing as t
from abc import ABC

import numpy as np
from numpy.typing import NDArray

SAMPLE_RATE: int = ...
N_FFT: int = ...
N_MEL: int = ...
HOP_LENGTH: int = ...
CHUNK_SIZE: int = ...

class SamplingType(ABC):
    def build(self) -> SamplingType: ...
    def to_enum(self) -> StrategyType: ...

class SamplingGreedyStrategy(SamplingType):
    best_of: int
    @t.overload
    def __init__(self, best_of: int) -> None: ...
    @t.overload
    def __init__(self) -> None: ...
    def with_best_of(self, best_of: int) -> SamplingGreedyStrategy: ...

class SamplingBeamSearchStrategy(SamplingType):
    beam_size: int
    patience: float
    @t.overload
    def __init__(self, beam_size: int, patience: float) -> None: ...
    @t.overload
    def __init__(self) -> None: ...
    def with_beam_size(self, beam_size: int) -> SamplingBeamSearchStrategy: ...
    def with_patience(self, patience: float) -> SamplingBeamSearchStrategy: ...

SAMPLING_GREEDY: StrategyType = ...
SAMPLING_BEAM_SEARCH: StrategyType = ...

class StrategyType(enum.Enum):
    SAMPLING_GREEDY = ...
    SAMPLING_BEAM_SEARCH = ...

class SamplingStrategies:
    type: StrategyType
    greedy: SamplingGreedyStrategy
    beam_search: SamplingBeamSearchStrategy
    @staticmethod
    def from_strategy_type(strategy_type: SamplingType) -> SamplingStrategies: ...
    @staticmethod
    def from_enum(strategy_enum: StrategyType) -> SamplingStrategies: ...
    # NOTE: the two below override are valid, but pyright does not like them.
    @t.overload
    def build(self) -> SamplingGreedyStrategy: ...  # type: ignore[override]
    @t.overload
    def build(self) -> SamplingBeamSearchStrategy: ...  # type: ignore[override]

class Params:
    num_threads: int
    def with_num_threads(self, num_threads: int) -> Params: ...
    num_max_text_ctx: int
    def with_num_max_text_ctx(self, max_text_ctx: int) -> Params: ...
    offset_ms: float
    def with_offset_ms(self, offset: float) -> Params: ...
    duration_ms: float
    def with_duration_ms(self, duration: float) -> Params: ...
    translate: bool
    def with_translate(self, translate: bool) -> Params: ...
    no_context: bool
    def with_no_context(self, no_context: bool) -> Params: ...
    single_segment: bool
    def with_single_segment(self, single_segment: bool) -> Params: ...
    print_special: bool
    def with_print_special(self, print_special: bool) -> Params: ...
    print_progress: bool
    def with_print_progress(self, print_progress: bool) -> Params: ...
    print_realtime: bool
    def with_print_realtime(self, print_realtime: bool) -> Params: ...
    print_timestamps: bool
    def with_print_timestamps(self, print_timestamps: bool) -> Params: ...
    token_timestamps: bool
    def with_token_timestamps(self, token_timestamps: bool) -> Params: ...
    timestamp_token_probability_threshold: float
    def with_timestamp_token_probability_threshold(self, thold_pt: float) -> Params: ...
    timestamp_token_sum_probability_threshold: float
    def with_timestamp_token_sum_probability_threshold(
        self, thold_ptsum: float
    ) -> Params: ...
    max_segment_length: int
    def with_max_segment_length(self, max_len: int) -> Params: ...
    split_on_word: bool
    def with_split_on_word(self, split_on_word: bool) -> Params: ...
    max_tokens: int
    def with_max_tokens(self, max_tokens: int) -> Params: ...
    speed_up: bool
    def with_speed_up(self, speed_up: bool) -> Params: ...
    audio_ctx: int
    def with_audio_ctx(self, audio_ctx: int) -> Params: ...
    prompt_tokens: int
    prompt_num_tokens: int
    language: str
    def with_language(self, language: str) -> Params: ...
    suppress_blank: bool
    def with_initial_prompt(self, initial_prompt: str) -> Params: ...
    initial_prompt: str
    def with_suppress_blank(self, suppress_blank: bool) -> Params: ...
    suppress_none_speech_tokens: bool
    def with_suppress_non_speech_tokens(
        self, suppress_non_speech_tokens: bool
    ) -> Params: ...
    temperature: float
    def with_temperature(self, temperature: float) -> Params: ...
    max_intial_timestamps: int
    def with_max_intial_timestamps(self, max_initial_ts: int) -> Params: ...
    length_penalty: float
    def with_length_penalty(self, length_penalty: float) -> Params: ...
    temperature_inc: float
    def with_temperature_inc(self, temperature_inc: float) -> Params: ...
    entropy_threshold: float
    def with_entropy_threshold(self, entropy_thold: float) -> Params: ...
    logprob_threshold: float
    def with_logprob_threshold(self, logprob_thold: float) -> Params: ...
    no_speech_threshold: float
    def with_no_speech_threshold(self, no_speech_thold: float) -> Params: ...
    def set_tokens(self, tokens: list[int]) -> None: ...
    def build(self) -> Params: ...
    @staticmethod
    def from_sampling_strategy(sampling_strategies: SamplingStrategies) -> Params: ...
    @staticmethod
    def from_enum(sampling_enum: StrategyType) -> Params: ...
    def on_new_segment(
        self, callback: t.Callable[[Context, int, T], None], userdata: T
    ) -> None: ...
    def on_progress(
        self, callback: t.Callable[[Context, int, T], None], userdata: T
    ) -> None: ...

T = t.TypeVar("T")

class Context:
    is_initialized: bool = ...
    lang_max_id: int
    n_len: int
    n_vocab: int
    n_text_ctx: int
    n_audio_ctx: int
    is_multilingual: bool
    eot_token: int
    sot_token: int
    prev_token: int
    solm_token: int
    not_token: int
    beg_token: int
    token_translate: int
    token_transcribe: int
    def lang_token(self, lang_id: int) -> int: ...
    def init_state(self) -> None: ...
    @staticmethod
    @t.overload
    def from_file(filename: str) -> Context: ...
    @staticmethod
    @t.overload
    def from_file(filename: str, no_state: bool = ...) -> Context: ...
    @staticmethod
    @t.overload
    def from_buffer(buffer: bytes) -> Context: ...
    @staticmethod
    @t.overload
    def from_buffer(buffer: bytes, no_state: bool = ...) -> Context: ...
    def free(self) -> None: ...
    @t.overload
    def pc_to_mel(self, pcm: NDArray[t.Any]) -> None: ...
    @t.overload
    def pc_to_mel(
        self,
        pcm: NDArray[t.Any],
        threads: int = ...,
        phase_vocoder: bool = ...,
    ) -> None: ...
    def set_mel(self, mel: NDArray[t.Any]) -> None: ...
    @t.overload
    def encode(self, offset: int) -> None: ...
    @t.overload
    def encode(self, offset: int, threads: int = ...) -> None: ...
    @t.overload
    def decode(self, token: list[int], n_past: int) -> None: ...
    @t.overload
    def decode(self, token: list[int], n_past: int, threads: int = ...) -> None: ...
    def tokenize(self, text: str, max_tokens: int) -> list[int]: ...
    def lang_str_to_id(self, lang: str) -> int: ...
    def lang_id_to_str(self, lang_id: int) -> str: ...
    @t.overload
    def lang_detect(self, offset_ms: int) -> list[float]: ...
    @t.overload
    def lang_detect(self, offset_ms: int, threads: int = ...) -> list[float]: ...
    def get_logits(self, segment: int) -> list[list[float]]: ...
    def token_to_str(self, token_id: int) -> str: ...
    def token_to_bytes(self, token_id: int) -> bytes: ...
    def full(self, params: Params, data: NDArray[t.Any]) -> int: ...
    def full_parallel(
        self, params: Params, data: NDArray[t.Any], num_processor: int
    ) -> int: ...
    def full_get_segment_text(self, segment: int) -> str: ...
    def full_get_token_data(self, segment: int, token: int) -> TokenData: ...
    def full_lang_id(self) -> int: ...
    def full_get_segment_start(self, segment: int) -> int: ...
    def full_get_segment_end(self, segment: int) -> int: ...
    def full_n_segments(self) -> int: ...
    def full_n_tokens(self, segment: int) -> int: ...
    def full_get_token_id(self, segment: int, token: int) -> int: ...
    def full_get_token_text(self, segment: int, token: int) -> str: ...
    def full_get_token_prob(self, segment: int, token: int) -> float: ...
    def reset_timings(self) -> None: ...
    def print_timings(self) -> None: ...
    def sys_info(self) -> None: ...

class WavFile:
    mono: NDArray[np.float32]
    stereo: tuple[NDArray[np.float32], NDArray[np.float32]]

class TokenData:
    id: int
    tid: int
    p: float
    plog: float
    pt: float
    ptsum: float
    t0: int
    t1: int
    vlen: float

def load_wav_file(filename: str) -> WavFile: ...
