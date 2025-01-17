import datetime
import os

import tensorflow as tf

from Base.crazy_data import CrazyData
from Base.data_loader import DataLoader
from Config.hyperparams import HyperParams
from net import Net

os.environ['CUDA_VISIBLE_DEVICES'] = '3'

hp = HyperParams()
loader = DataLoader(hp, mode='train')
crazyData = CrazyData(
    pid='jCou', ticket='e0Tr5orRjqYpZ5754CkLKxjgt38nCAG3cD7cSl774lPXC2qjN0AFjRztOXkoxONc')

tf.reset_default_graph()

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
with tf.Session(config=config) as sess:
    n = Net(hp=hp)

    sess.run(tf.global_variables_initializer())

    saver = tf.train.Saver()
    saver.restore(sess, os.path.join(hp.logdir, 'epoch3.ckpt'))

    for epoch in range(4, hp.epoch):
        index = 0
        print('epoch', epoch)
        for VGG, C3D, HIS, QUE, ANS, CAN, ANS_ID in loader.get_batch_data():
            _, mean_loss, pAt1, pAt5, mrr, meanRank = sess.run(
                (n.train_operation, n.mean_loss, n.pAt1, n.pAt5, n.mrr, n.meanRank), feed_dict={
                    n.VGG: VGG,
                    n.C3D: C3D,
                    n.HIS: HIS,
                    n.QUE: QUE,
                    n.ANS: ANS,
                    n.CAN: CAN,
                    n.ANS_ID: ANS_ID,
                })
            if index % 100 == 0:
                print(str(datetime.datetime.now()),
                      'index:', index,
                      'loss:', mean_loss,
                      'p@1:', pAt1,
                      'p@5:', pAt5,
                      'mrr:', mrr,
                      'mr', meanRank)
                crazyData.push([
                    dict(label='loss@e%s' % epoch, value=int(mean_loss * 1000)),
                    dict(label='pAt1@e%s' % epoch, value=int(pAt1 * 10000)),
                    dict(label='pAt5@e%s' % epoch, value=int(pAt5 * 10000)),
                    dict(label='mrr@e%s' % epoch, value=int(mrr * 10000)),
                    dict(label='meanRank@e%s' % epoch, value=int(meanRank * 1000)),
                ])
            index += 1
        print('total index', index, 'start saving!')
        saver.save(sess, os.path.join(hp.logdir, 'epoch{0}.ckpt'.format(epoch)))
