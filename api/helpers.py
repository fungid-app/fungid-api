import imp
from fastai.data.external import *
from fastbook import *
from fastai.data.external import *
import torch.nn.functional as F
from .observation import Observation


def get_x(a):
    return a[0]


def get_y(a):
    return a[1]


def accuracy_species(inp, targ, axis=-1):
    pred, targ = flatten_check(inp.argmax(dim=axis), targ)
    return (pred == targ).float().mean()


def top_5(inp, targ, axis=-1):
    return top_n(5, inp, targ, axis)


def top_10(inp, targ, axis=-1):
    return top_n(10, inp, targ, axis)


def top_n(n, inp, targ, axis=-1):
    _, idx = torch.topk(inp, n)
    return (idx == targ.unsqueeze(axis)).any(axis).float().mean()


def accuracy_tax(tax_targets, inp, targ, axis=-1):
    temp = [torch.argmax(x) for x in inp]
    new_inp = tensor([tax_targets[x] for x in temp])
    new_targ = tensor([tax_targets[x] for x in targ])
    return (new_inp == new_targ).float().mean()


def accuracy_family(inp, targ, axis=-1):
    return accuracy_tax(family_targets, inp, targ, axis)


def accuracy_genus(inp, targ, axis=-1):
    return accuracy_tax(genus_targets, inp, targ, axis)


def cross_entropy_species(input, target, weight=None, size_average=None, ignore_index=-100,
                          reduce=None, reduction='mean'):
    input_p = torch.softmax(input, dim=-1)
    return F.nll_loss(torch.log(input_p), target, None, None, ignore_index, None, reduction)


def cross_entropy_tax(tax_targets, target_dims, input, target, weight=None, size_average=None, ignore_index=-100,
                      reduce=None, reduction='mean'):

    # softmax to convert scores to probabilities
    input_p = torch.softmax(input, dim=1)

    # Sum the probabilities for each taxonomy classification
    # Could not compile: new_input = scatter_add(input_p, tax_targets)
    tax_index = tax_targets.repeat(len(input_p), 1)
    new_input = torch.zeros(len(input_p), target_dims,
                            dtype=input_p.dtype, device='cuda:0')
    new_input.scatter_add_(1, tax_index, input_p)
    # Create the new target
    new_target = TensorCategory(tax_targets[target].long())
    return F.nll_loss(torch.log(new_input), new_target, None, None, ignore_index, None, reduction)


def cross_entropy_family(input, target, weight=None, size_average=None, ignore_index=-100,
                         reduce=None, reduction='mean'):
    return cross_entropy_tax(family_targets, family_dims, input, target, weight, size_average, ignore_index, reduce, reduction)


def cross_entropy_genus(input, target, weight=None, size_average=None, ignore_index=-100,
                        reduce=None, reduction='mean'):
    return cross_entropy_tax(genus_targets, genus_dims, input, target, weight, size_average, ignore_index, reduce, reduction)


def joint_loss(input, target, w=1, weight=None, size_average=None, ignore_index=-100,
               reduce=None, reduction='mean'):
    ce_species = cross_entropy_species(input, target, weight=None, size_average=None, ignore_index=-100,
                                       reduce=None, reduction='mean')

    ce_genus = cross_entropy_genus(input, target, weight=None, size_average=None, ignore_index=-100,
                                   reduce=None, reduction='mean')

    # Linear combination of the cross-entropy scores at the 2 levels in hierarchy.
    return w*ce_species+(1-w)*ce_genus


def get_tab_model_data(data):
    tab_columns = ['kg', 'elu_class1', 'elu_class2', 'elu_class3',
                   'decimallatitude', 'decimallongitude', 'species', 'normalized_month', 'season']
    return data[tab_columns].copy()


def get_img_model_data(data):
    img_data = data.copy()
    img_data['img'] = 'dbs/images/224/' + \
        data.gbifid.astype(str) + '-' + \
        data.imgid.astype(int).astype(str) + '.png'
    return img_data[['img', 'species']]


def get_results(learner, data):
    row, clas, probs = learner.predict(data)
    # print(clas)
    return probs


def get_bounding_box(lat, lon, dist):
    latdiff = (180 / math.pi) * (dist / 6378137)
    londiff = (180 / math.pi) * (dist / 6378137) / math.cos(lat)
    return (lat - latdiff, lon - londiff), (lat + latdiff, lon + londiff)


def get_db_species(conn, observation, dist):
    p1, p2 = get_bounding_box(tab_item.decimallatitude,
                              tab_item.decimallongitude, dist)
    print(p1, p2)
    cursor = conn.execute("""
    SELECT species, COUNT(*)
    FROM validobservations v 
    JOIN trainingspecies t ON v.specieskey = t.specieskey
    WHERE decimallatitude BETWEEN ? AND ? 
    AND decimallongitude BETWEEN ? AND ? 
    GROUP BY 1 ORDER BY 2;""",
                          (p1[0], p2[0], p1[1], p2[1]))
    results = cursor.fetchall()
    print(len(results))


def obs_from_series(series: pd.Series) -> Observation:
    image = PILImage.create(series.img)
    if image is None:
        raise Exception("Could not load image: ", series.img)

    date = datetime.strptime(series.eventdate, '%Y-%m-%d %H:%M:%S')
    return Observation(image, series.decimallatitude, series.decimallongitude,
                       date, series.kg, series.elu_class1, series.elu_class2, series.elu_class3)
