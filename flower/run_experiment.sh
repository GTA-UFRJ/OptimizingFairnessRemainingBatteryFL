#!/binæbash
FIXED_ROUNDS=$1
VARIABLE_ROUNDS=$2

LOGDIR=logs/fixed_${FIXED_ROUNDS}_variable_${VARIABLE_ROUNDS}
mkdir -p $LOGDIR

rm -rf --interactive=never initial_clients 
mkdir initial_clients

rm -rf --interactive=never wf_solver
cp -r ../wf_solver .

rm -rf --interactive=never MNIST
cp -r ../data/MNIST .

sudo docker compose -f compose.yaml up --build
cat $LOGDIR/server.log
