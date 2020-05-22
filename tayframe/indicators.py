#!/usr/bin/env python3

from functools import reduce


def moving_avg(df, key, lag):
    '''
    Simple moving average indicator.

    Params:
      - df (list of dicts): input dataframe.
      - key (str): dataframe row key to calc indicator over.
      - lag (int): calculation period.

    Returns:
      - (list): sma timeseries list. Will be right-aligned with df.
    '''
    def _sma(key, window):
        values = list(map(lambda w: w[key], window))
        avg = round(reduce(lambda a, b: a + b, values) / len(values), 2)
        return avg

    return [
        _sma(key, df[i: i + lag + 1])
        for i in range(len(df) - lag)
    ]


def ema(df, key, lag):
    '''
    Exponential moving average indicator.

    Params:
      - df (list of dicts): input dataframe.
      - key (str): dataframe row key to calc indicator over.
      - lag (int): calculation period.

    Returns:
      - (list): ema timeseries list. Will be right-aligned with df.
    '''
    def calc_ema(index, df, emas, mult):
        return round(((df[index][key] - emas[-1]) * mult) + emas[-1], 2)

    avg = moving_avg(df, key, lag)[0]
    multiplier = (2.0 / (lag + 1))

    emas = [avg]
    [
        emas.append(calc_ema(i, df, emas, multiplier))
        for i in range(lag + 1, len(df))
    ]
    return emas


def macd(df, slow, fast, signal):
    '''
    MACD indicator.

    Params:
      - df (list of dicts): input dataframe.
      - slow (int): slow ema lag.
      - fast (int): fast ema lag.
      - signal (int): signal lag.

    Returns:
      - (list): timeseries list corresponding to the macd histogram.
    '''
    def calc_macd_line(slow, fast):
        return [
            round(fast[i] - slow[i], 2)
            for i in range(len(slow))
        ]

    def calc_signal(index, line, signal, mult):
        next_sig = ((line[index] - signal[-1]) * mult) + signal[-1]
        return round(next_sig, 2)

    slowema = ema(df, 'c', slow)
    fastema = ema(df, 'c', fast)[-1 * len(slowema):]
    macd_line = calc_macd_line(slowema, fastema)
    multiplier = (2.0 / (signal + 1))

    sigema = [macd_line[0]]
    [
        sigema.append(calc_signal(i, macd_line, sigema, multiplier))
        for i in range(signal + 1, len(macd_line))
    ]
    macd_final = macd_line[-1 * len(sigema):]

    return [
        round(macd_final[i] - sigema[i], 2)
        for i in range(len(sigema))
    ]


def atr(df, lag, normalize=False):
    '''
    Average true range (ATR) indicator.

    Params:
      - df (list): input dataframe.
      - lag (int): calculation period.
      - normalize (bool): flag to normalize atr based on % vs price.

    Returns:
      - (list): atr timeseries list.
    '''
    def _true_range(window):
        divisor = (1.0 * float(not normalize)) + \
            ((float(normalize) * window[-1]['c']))

        tr1 = window[-1]['h'] - window[-1]['l']
        tr2 = window[-1]['h'] - window[-2]['c']
        tr3 = window[-1]['l'] - window[-2]['c']
        return max(tr1, tr2, tr3) / divisor

    def _sma(window):
        avg = round(reduce(lambda a, b: a + b, window) / len(window), 2)
        return avg

    tr = [
        _true_range(df[i: i + 2])
        for i in range(len(df) - 1)
    ]
    return [
        _sma(tr[i: i + lag + 1])
        for i in range(len(tr) - lag)
    ]


def gaps(df):
    '''
    Calculate the overnight gap (diff between close and open).

    Params:
      - df (list): input dataframe.

    Returns:
      - (list): timeseries list of gaps.
    '''
    return [
        (round(df[i]['o'] - df[i - 1]['c'], 2))
        for i in range(1, len(df))
    ]


def rsi(df, lag):
    '''
    Relative Strength Indicator (RSI).

    Params:
      - df (list): input dataframe.
      - lag (int): calculation period.

    Returns:
      - (list): timeseries RSI list.
    '''
    def avg_gain():
        gains = [
            df[i]['c'] - df[i - 1]['c']
            if df[i]['c'] >= df[i - 1]['c'] else 0.0
            for i in range(1, len(df))
        ]
        avg_gain = [sum(gains[:lag]) / float(lag)]
        [
            avg_gain.append(((avg_gain[-1] * 13) + gain) / 14.0)
            for gain in gains[lag:]
        ]
        return avg_gain

    def avg_loss():
        losses = [
            abs(df[i]['c'] - df[i - 1]['c'])
            if df[i]['c'] < df[i - 1]['c'] else 0.0
            for i in range(1, len(df))
        ]
        avg_loss = [sum(losses[:lag]) / float(lag)]
        [
            avg_loss.append(((avg_loss[-1] * 13) + loss) / 14.0)
            for loss in losses[lag:]
        ]
        return avg_loss

    gains = avg_gain()
    losses = avg_loss()

    raw_rsi = [
        round(100 - (100 / (1 + (gains[i] / losses[i]))), 2)
        for i in range(len(gains))
    ]
    df = df[-1 * len(raw_rsi):]

    return [raw_rsi[i] for i in range(len(df))]


def percent_change(df, lag):
    '''
    % change between for a given lookback.

    Params:
      - df (list): input dataframe.
      - lag (int): calculation period.

    Returns:
      - (list): % change timeseries list.
    '''
    def _pc(window):
        today = float(window[-1]['c'])
        compare = float(window[0]['c'])
        change = ((today - compare) / compare) * 100
        return round(change, 2)

    return [
        _pc(df[i: i + lag + 1])
        for i in range(len(df) - lag)
    ]


def new_high(df):
    '''
    New high indicator. Determines if the current row is a new high in relation
    to all previous rows.

    Params:
      - df: input dataframe.

    Returns:
      - (list of bools): timeseries list for new highs.
    '''
    def _is_high(window):
        high = max(window, key=lambda d: d['c'])['c']
        return (window[-1]['c'] == high)

    return [
        _is_high(df[:i + 1])
        for i in range(len(df))
    ]


def frequency(df, keys, lag):
    '''
    Frequency of occurence. Finds the frequency a set of keys are True for the
    given lag window.

    NOTE: this function takes a list of keys to calculate over. Each column name
          provided MUST only contain the values True or False.

    Params:
      - df (list): input dataframe.
      - keys (list): list of keys to include in the frequency calc.
      - lag (int): lag window.

    Returns:
      - (list) timeseries including freq count for rolling window.
    '''
    def _freq(window):
        values = [
            [d[k] for d in window]
            for k in keys
        ]
        frequencies = list(map(lambda v: v.count(True), values))
        return sum(frequencies)

    return [
        _freq(df[i: i + 31])
        for i in range(len(df) - 30)
    ]
