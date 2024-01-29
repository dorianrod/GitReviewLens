from ..transcoder import Transcoder


def test_transcoder():
    transcoder = Transcoder('type1', {'a': '1', 'b': '2'})
    assert transcoder.transcode('a') == '1'
    assert transcoder.transcode('b') == '2'
    assert transcoder.transcode('c') == 'c'


def test_transcoder_with_default_value():
    transcoder = Transcoder('type1', {'a': '1', '': 'default'})
    assert transcoder.transcode('a') == '1'
    assert transcoder.transcode('b') == 'default'


def test_transcoder_with_start_value():
    transcoder = Transcoder('type1', {'mysuperfeature': '1'})
    assert (
        transcoder.transcode_by_startvalue('mysuperfeature/is_something_for_sure')
        == '1'
    )
    assert (
        transcoder.transcode_by_startvalue('other/is_not_transcoded')
        == 'other/is_not_transcoded'
    )


def test_transcoder_with_start_value_default():
    transcoder = Transcoder('type1', {'mysuperfeature': '1', '': 'default'})
    assert (
        transcoder.transcode_by_startvalue('mysuperfeature/is_something_for_sure')
        == '1'
    )
    assert transcoder.transcode_by_startvalue('other/is_not_transcoded') == 'default'
