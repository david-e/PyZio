import PyZio as zio


if __name__ == '__main__':
    devs = zio.utils.list_devices()
    chan0, chan1, chan2 = devs[0].cset[0].channels[:3]
    chan0.enable = True
    print devs[0].to_json()
    for chan, block in zio.utils.wait_for_blocks([chan0, chan1, chan2], 10):
        print chan.name, block
        break