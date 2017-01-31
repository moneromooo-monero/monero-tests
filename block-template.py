import math
import random

ACCEPT_THRESHOLD = .99
NUM_PRIO_FEE_IN_POOL = 9
MIN_TX_SIZE = 7500
MAX_TX_SIZE = 7550
ALREADY_GENERATED_COINS = long(13800000 * 1000000000000)
MIN_BLOCK_SIZE_MEDIAN = 60000
MIN_SUBSIDY_PER_BLOCK = 600000000000
BASE_FEE_PER_KB = 2000000000

def median(l):
  if len(l) == 0:
    return 0
  if len(l) == 1:
    return l[0]
  n = len(l) / 2
  l.sort()
  if len(l) % 2 == 1:
    return l[n]
  else:
    return (l[n-1] + l[n]) / 2

def get_block_reward(median_size, current_block_size, already_generated_coins):
  base_reward = (0xffffffffffffffff - already_generated_coins) >> (20-(2-1))
  if base_reward < MIN_SUBSIDY_PER_BLOCK:
    base_reward = MIN_SUBSIDY_PER_BLOCK
  full_reward_zone = MIN_BLOCK_SIZE_MEDIAN
  if median_size < full_reward_zone:
    median_size = full_reward_zone
  if current_block_size <= median_size:
    return base_reward
  if current_block_size > 2 * median_size:
    raise 1
  multiplicand = 2 * median_size - current_block_size
  multiplicand = multiplicand *current_block_size
  product = base_reward * multiplicand
  reward = product / median_size
  reward = reward / median_size
  return reward

def get_block_reward_f(median_size, current_block_size, already_generated_coins):
  return get_block_reward(median_size, current_block_size, already_generated_coins) / 1e12

def get_last_100(blocks):
  if len(blocks) < 100:
    return blocks
  return blocks[-100:]

def get_median_size_of_last_100_blocks(blocks):
  m = median(get_last_100(blocks))
  if m < MIN_BLOCK_SIZE_MEDIAN:
    return MIN_BLOCK_SIZE_MEDIAN
  return m

def get_fee(size, mul):
  size = int((size + 1023) / 1024)
  return size * BASE_FEE_PER_KB * mul

def get_block_template_size(template):
  return sum(template)

def build_block_template(blocks, already_generated_coins, tx_size_min, tx_size_max):
  best_coinbase = 0
  total_size = 0
  fee = 0
  median_size = get_median_size_of_last_100_blocks(blocks)
  max_total_size = 2 * median_size - 260
  template=[]
  #print 'Building block template, median %u' % median_size
  for N in range(500):
    tx_size = tx_size_min + int(random.random() * (tx_size_max - tx_size_min))
    tx_fee = get_fee(tx_size, 20 if N < NUM_PRIO_FEE_IN_POOL else 1)
    #print 'trying tx %u, max_total_size %u, test %u' % (tx_size, max_total_size, total_size + tx_size)
    if max_total_size < total_size + tx_size:
      continue
    block_reward = get_block_reward(median_size, total_size + tx_size, already_generated_coins)
    coinbase = block_reward + fee + tx_fee
    if coinbase < ACCEPT_THRESHOLD * best_coinbase:
      continue
    template.append(tx_size)
    total_size += tx_size
    fee += tx_fee
    best_coinbase = coinbase
  return template, best_coinbase, fee

#print "Block reward at 0: %f" % get_block_reward_f(0, 1000, 0)
#l = [1, 4, 9, 2, 4, 7, 2, 5]
#print "Median of %s: %s" % (l, median(l))
#print "Per kB fee: %f" % (get_fee(1023, 1) / 1e12)

blocks = []
already_generated_coins = ALREADY_GENERATED_COINS
for h in range(10000):
  template, coinbase, fee = build_block_template(blocks, already_generated_coins, MIN_TX_SIZE, MAX_TX_SIZE)
  blocks.append(get_block_template_size(template))
  already_generated_coins = already_generated_coins + coinbase - fee
  print "[%5u] Adding template with %u txes, size %u, coinbase %f, fee %f, median %u, coins %f" % (h, len(template), get_block_template_size(template), coinbase/1e12, fee/1e12, get_median_size_of_last_100_blocks(blocks), already_generated_coins / 1e12)

