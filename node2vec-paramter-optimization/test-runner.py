from node2vec.py import makeNodeModel, getAllNodes


# Write a function like this called 'main'
def main(job_id, params):
  print 'Anything printed here will end up in the output directory for job #:', str(job_id)
  print params

  # generate model with params
  pqRatio = float(params["PQRatio"][0])
  p = 1
  q = p*pqRatio
  
  l = int(params["l"][0])
  r = int(params["r"][0])
  k = int(params["k"][0])
  undirected = False # TODO
  unweighted = False # TODO
  workers = 2 # TODO
  nodes = getAllNodes()
  model = makeNodeModel(p, q, l, r, k, undirected, unweighted, workers, nodes)

  # save model using a file name that identifies the settings
  model_name = "test"
  model.save_word2vec_format(model_name)

  

  return 1