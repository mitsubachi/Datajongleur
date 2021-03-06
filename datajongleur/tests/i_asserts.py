def quantity(iq, example_result):
  """
  This test applies `pars pro toto`: instead of explicitly testing all
  arithmetic operations and test cases, a representative subset is tested.
  """
  assert type(iq.max()) == iq._arithmetic_return_type
  assert type(iq * iq) == iq._arithmetic_return_type
  assert (iq * iq).max() == example_result
  return True

def interval(iq, start, stop):
  assert iq.start == start
  assert iq.stop == stop
  assert iq.length == stop - start
  return True

def sampled_signal(iq):
  assert len(iq) == len(iq.signal)
  assert len(iq) == len(iq.base)
  assert len(iq) == iq.n_sampling_points
  return True

def regularly_sampled_signal(iq, start, stop):
  assert assert_interval(iq, start, stop)
  assert assert_sampled_signal(iq)
  assert iq.sampling_rate == iq.n_sampling_points/iq.length
  assert iq.step_size == 1 / iq.sampling_rate
  return True

