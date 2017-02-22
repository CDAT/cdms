export UVCDAT_ANONYMOUS_LOG=False
export PATH=${HOME}/miniconda/bin:${PATH}
echo "CIRCLE CI BRANCH:"$CIRCLE_BRANCH
echo "CI_PULL_REQUESTS"$CI_PULL_REQUESTS
echo "CI_PULL_REQUEST"$CI_PULL_REQUEST
python run_tests.py 
if [ $_ == 0 ]; then ./conda_upload.sh
