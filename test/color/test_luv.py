import pytest

import kornia
import kornia.testing as utils  # test utils

import torch
from torch.autograd import gradcheck
from torch.testing import assert_allclose


class TestRgbToLuv:

    @pytest.mark.parametrize("batch_size", [None, 1, 2, 5])
    def test_rgb_to_luv(self, batch_size, device):

        data = torch.tensor([[[[0.13088040, 0.54399723, 0.69396782, 0.63581685, 0.09902618],
                               [0.59459005, 0.74215373, 0.89662376, 0.25920381, 0.89937686],
                               [0.29857584, 0.28139791, 0.16441015, 0.55507519, 0.06124221],
                               [0.40908658, 0.10261389, 0.01691456, 0.76006799, 0.32971736]],

                              [[0.60354551, 0.76201361, 0.79009938, 0.91742945, 0.60044175],
                               [0.42812678, 0.18552390, 0.04186043, 0.38030245, 0.15420346],
                               [0.13552373, 0.53955473, 0.79102736, 0.49050815, 0.75271446],
                               [0.39861023, 0.80680277, 0.82823833, 0.54438462, 0.22063386]],

                              [[0.63231256, 0.18316011, 0.84317145, 0.59529881, 0.15297393],
                               [0.59235313, 0.36617295, 0.34600773, 0.40304737, 0.61720451],
                               [0.46040250, 0.42006640, 0.54765106, 0.48982632, 0.13914755],
                               [0.58402964, 0.89597990, 0.98276161, 0.25019163, 0.69285921]]]])

        # Reference output generated using skimage: rgb2luv(data)

        luv_ref = torch.tensor([[[[58.02612686, 72.48876190, 79.75208282, 86.38912964, 55.25164032],
                                  [51.66668701, 43.81214523, 48.93865585, 39.03804398, 52.55152512],
                                  [23.71140671, 52.38661957, 72.54607391, 53.89587402, 67.94892883],
                                  [45.02897263, 75.98315430, 78.25762177, 61.85069656, 33.77972794]],

                                 [[-41.55438232, -28.05948639, -13.54032803, -35.42317200, -49.27433014],
                                  [21.34596062, 94.13956451, 137.11340332, -14.69241238, 102.94833374],
                                  [9.55611229, -30.01761436, -58.94236755, 9.83261871, -62.96137619],
                                  [-1.55336237, -55.22497559, -56.21067810, 43.76751328, 1.46367633]],

                                 [[-15.29427338, 77.81495667, -13.74480152, 52.17128372, 60.92724228],
                                     [-27.01125526, -1.72837746, 6.57535267, -7.83582020, -38.45543289],
                                     [-50.89970779, 17.65329361, 36.54148102, 2.25501800, 78.93702698],
                                     [-38.39783859, -31.71204376, -46.63606644, 50.16629410, -84.74416351]]]])

        data.to(device)
        luv_ref.to(device)

        if batch_size is not None:
            data = data.repeat(batch_size, 1, 1, 1)
            luv_ref = luv_ref.repeat(batch_size, 1, 1, 1)

        luv = kornia.color.RgbToLuv()
        out = luv(data)
        assert_allclose(out, luv_ref)

    def test_grad(self, device):

        data = torch.rand(2, 3, 4, 5).to(device)
        data = utils.tensor_to_gradcheck_var(data)
        assert gradcheck(kornia.color.RgbToLuv(), (data,), raise_exception=True)

    @pytest.mark.parametrize("input_shape", [(2, 2), (3, 3, 5, 3, 3)])
    def test_shape(self, input_shape, device):
        with pytest.raises(ValueError):
            luv = kornia.color.RgbToLuv()
            out = luv(torch.ones(*input_shape).to(device))

    def test_inverse(self, device):
        data = torch.rand(3, 4, 5).to(device)
        luv = kornia.color.LuvToRgb()
        rgb = kornia.color.RgbToLuv()

        data_out = luv(rgb(data))
        assert_allclose(data_out, data)

    @pytest.mark.skip(reason="turn off all jit for a while")
    def test_jit(self, device):

        data = torch.rand((2, 3, 4, 5)).to(device)
        luv = kornia.color.rgb_to_luv
        luv_jit = torch.jit.script(kornia.color.rgb_to_luv)
        assert_allclose(luv_jit(data), luv(data))


class TestLuvToRgb:

    @pytest.mark.parametrize("batch_size", [None, 1, 2, 5])
    def test_rgb_to_luv(self, batch_size, device):

        data = torch.tensor([[[[50.21928787, 23.29810143, 14.98279190, 62.50927353, 72.78904724],
                               [70.86846924, 68.75330353, 52.81696701, 76.17090607, 88.63134003],
                               [46.87160873, 72.38699341, 37.71450806, 82.57386780, 74.79967499],
                               [77.33016968, 47.39180374, 61.76217651, 90.83254242, 86.96239471]],

                              [[65.81327057, -3.69859719, 0.16971001, 14.86583614, -65.54960632],
                               [-41.03258133, -19.52661896, 64.16155243, -58.53935242, -71.78411102],
                               [112.05227661, -60.13330460, 43.07910538, -51.01456833, -58.25787354],
                               [-62.37575531, 50.88882065, -39.27450943, 17.00958824, -24.93779755]],

                              [[-69.53346252, -73.34986877, -11.47461891, 66.73863220, 70.43983459],
                               [51.92737579, 58.77009583, 45.97863388, 24.44452858, 98.81991577],
                               [-7.60597992, 78.97976685, -69.31867218, 67.33953857, 14.28889370],
                               [92.31149292, -85.91405487, -32.83668518, -23.45091820, 69.99038696]]]])
        # Reference output generated using skimage: luv2rgb(data)

        rgb_ref = torch.tensor([[[[0.78923208, 0.17048222, 0.14947766, 0.65528989, 0.07863078],
                                  [0.41649094, 0.55222923, 0.72673196, 0.21939684, 0.34298307],
                                  [0.82763243, 0.24021322, 0.58888060, 0.47255886, 0.16407511],
                                  [0.30320778, 0.72233224, 0.21593384, 0.98893607, 0.71707106]],

                                 [[0.20532851, 0.13188709, 0.13879408, 0.59964627, 0.80721593],
                                     [0.75411713, 0.70656943, 0.41770950, 0.82750136, 0.99659365],
                                     [0.12436169, 0.79804462, 0.10958754, 0.89803618, 0.81000644],
                                     [0.85726571, 0.17667055, 0.63285238, 0.85567462, 0.91538441]],

                                 [[0.73985511, 0.59308004, 0.21156698, 0.03804367, 0.32732114],
                                     [0.42489606, 0.33011687, 0.12804756, 0.64905322, 0.25216782],
                                     [0.41637793, 0.22158240, 0.63437861, 0.46121466, 0.68336427],
                                     [0.06325728, 0.78878325, 0.74280596, 0.99514300, 0.47176042]]]])

        data.to(device)
        rgb_ref.to(device)

        if batch_size is not None:
            data = data.repeat(batch_size, 1, 1, 1)
            rgb_ref = rgb_ref.repeat(batch_size, 1, 1, 1)

        rgb = kornia.color.LuvToRgb()
        out = rgb(data)
        assert_allclose(out, rgb_ref)

    def test_grad(self, device):

        data = kornia.rgb_to_luv(torch.rand(2, 3, 4, 5).to(device))
        data = utils.tensor_to_gradcheck_var(data)
        assert gradcheck(kornia.color.LuvToRgb(), (data,), raise_exception=True)

    @pytest.mark.parametrize("input_shape", [(2, 2), (3, 3, 5, 3, 3)])
    def test_shape(self, input_shape, device):
        with pytest.raises(ValueError):
            rgb = kornia.color.LuvToRgb()
            out = rgb(torch.ones(*input_shape).to(device))

    def test_inverse(self, device):
        data = torch.rand(3, 11, 15).to(device)
        luv = kornia.color.LuvToRgb()
        rgb = kornia.color.RgbToLuv()

        data_out = rgb(luv(data))
        assert_allclose(data_out, data)

    @pytest.mark.skip(reason="turn off all jit for a while")
    def test_jit(self, device):

        data = torch.rand((2, 3, 4, 5)).to(device)
        rgb = kornia.color.luv_to_rgb
        rgb_jit = torch.jit.script(kornia.color.luv_to_rgb)
        assert_allclose(rgb_jit(data), rgb(data))
