"""

This Script Uses a Google Cloud Storage Workflow but does not upload any intermediate steps.
This script will still use Google Earth Engine to create data and the model but will upload results to GCS.
To upload and access data through Google Earth Engine, use the main_ee.py script instead.
To upload and access data through Google Cloud Storage, use the main_gcs.py script instead.
This script will not upload any intermediate steps to GCS.

"""

import ee
from src.setup.setup import setup_ee
from src.get_roi.get_roi import get_roi_ee
from src.make_study_area.make_study_area import make_study_area_ee
from src.make_training.make_training import make_training_ee
from src.make_testing.make_testing import make_testing_ee
from src.test_model.test_model import test_model_ee
from src.train_model.train_model import train_model_ee
from src.mask_water.mask_water import mask_water_ee
from src.gcs_upload.gcs_upload import check_and_export_geotiff_to_bucket
from config import (DEBUG, BUCKET_NAME, RESOLUTION, ROI_NAME, ANALYSIS_YEAR)



# step 1: Setup EE
folder_name = setup_ee(debug=DEBUG)

# step 2: get ROI from URL
roi = get_roi_ee(folder_name, debug=DEBUG)

# step 3: define the study area
study_area = make_study_area_ee(roi, folder_name, debug=DEBUG)

# # step 4: make the training data
multiband_raster, start_date, end_date = make_training_ee(study_area, roi, folder_name, debug=DEBUG)

# step 5: make the testing data

testing_data = make_testing_ee(roi, start_date, end_date, folder_name, debug=DEBUG)

# step 5: train the model
change_classifier = train_model_ee(multiband_raster, study_area, folder_name, debug=True)

# step 6: test the model
classified_image = test_model_ee(testing_data, roi, change_classifier, folder_name, debug=True)

# step 7:  mask water to low fire probability
water_masked = mask_water_ee(classified_image, testing_data, roi, folder_name, debug= DEBUG)

water_masked_asset_name = f"classified_image_water_mask_{ROI_NAME}_{ANALYSIS_YEAR}_{RESOLUTION}m"

# step 6: upload the model to GCS
#check_and_export_geotiff_to_bucket(BUCKET_NAME, water_masked_asset_name, water_masked, RESOLUTION)