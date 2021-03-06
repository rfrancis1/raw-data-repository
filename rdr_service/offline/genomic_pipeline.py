import logging

from rdr_service.dao.genomics_dao import GenomicSetDao
from rdr_service.genomic import (
    genomic_biobank_manifest_handler,
    genomic_set_file_handler,
    validation,
    genomic_center_manifest_handler
)
from rdr_service.genomic.genomic_job_controller import GenomicJobController
from rdr_service.participant_enums import (
    GenomicSetStatus,
    GenomicJob,
    GenomicManifestTypes
)
import rdr_service.config as config


def process_genomic_water_line():
    """
  Entrypoint, executed as a cron job
  """
    genomic_set_id = genomic_set_file_handler.read_genomic_set_from_bucket()
    if genomic_set_id is not None:
        logging.info("Read input genomic set file successfully.")
        dao = GenomicSetDao()
        validation.validate_and_update_genomic_set_by_id(genomic_set_id, dao)
        genomic_set = dao.get(genomic_set_id)
        if genomic_set.genomicSetStatus == GenomicSetStatus.VALID:
            genomic_biobank_manifest_handler.create_and_upload_genomic_biobank_manifest_file(genomic_set_id)
            logging.info("Validation passed, generate biobank manifest file successfully.")
        else:
            logging.info("Validation failed.")
        genomic_set_file_handler.create_genomic_set_status_result_file(genomic_set_id)
    else:
        logging.info("No file found or nothing read from genomic set file")

    genomic_biobank_manifest_handler.process_genomic_manifest_result_file_from_bucket()
    genomic_center_manifest_handler.process_genotyping_manifest_files()


def new_participant_workflow():
    """
    Entrypoint for New Participant Workflow,
    Sources from newly-created biobank_stored_samples
    from the BiobankSamplesPipeline.
    """
    with GenomicJobController(GenomicJob.NEW_PARTICIPANT_WORKFLOW) as controller:
        controller.run_new_participant_workflow()


def genomic_centers_manifest_workflow():
    """
    Entrypoint for Ingestion:
        Biobank to Genomic Centers Manifest (AW1)
    """
    with GenomicJobController(GenomicJob.BB_GC_MANIFEST,
                              bucket_name=None,
                              bucket_name_list=config.GENOMIC_CENTER_BUCKET_NAME,
                              sub_folder_name=config.GENOMIC_GENOTYPING_SAMPLE_MANIFEST_FOLDER_NAME
                              ) as controller:
        controller.run_genomic_centers_manifest_workflow()


def genomic_centers_aw1f_manifest_workflow():
    """
        Entrypoint for Ingestion:
            Failure Manifest (AW1F)
        """
    with GenomicJobController(GenomicJob.AW1F_MANIFEST,
                              bucket_name=None,
                              bucket_name_list=config.GENOMIC_CENTER_BUCKET_NAME,
                              sub_folder_name=config.GENOMIC_AW1F_SUBFOLDER
                              ) as controller:
        controller.run_aw1f_manifest_workflow()


def ingest_genomic_centers_metrics_files():
    """
    Entrypoint for GC Metrics File Ingestion subprocess of genomic_pipeline.
    """
    with GenomicJobController(GenomicJob.METRICS_INGESTION) as controller:
        controller.ingest_gc_metrics()


def reconcile_metrics_vs_manifest():
    """
    Entrypoint for GC Metrics File reconciliation
    against Manifest subprocess of genomic_pipeline.
    """
    with GenomicJobController(GenomicJob.RECONCILE_MANIFEST) as controller:
        controller.run_reconciliation_to_manifest()


def reconcile_metrics_vs_genotyping_data():
    """
    Entrypoint for GC Metrics File reconciliation
    Genotyping Files (Array) vs Listed in Manifest.
    """
    with GenomicJobController(GenomicJob.RECONCILE_GENOTYPING_DATA) as controller:
        controller.run_reconciliation_to_genotyping_data()


def reconcile_metrics_vs_sequencing_data():
    """
    Entrypoint for GC Metrics File reconciliation
    Sequencing Files (Array) vs Listed in Manifest.
    """
    with GenomicJobController(GenomicJob.RECONCILE_SEQUENCING_DATA) as controller:
        controller.run_reconciliation_to_sequencing_data()


def gem_a1_manifest_workflow():
    """
    Entrypoint for GEM A1 Workflow
    First workflow in GEM Workflow
    """
    with GenomicJobController(GenomicJob.GEM_A1_MANIFEST,
                              bucket_name=config.GENOMIC_GEM_BUCKET_NAME) as controller:
        controller.generate_manifest(GenomicManifestTypes.GEM_A1, _genome_type=config.GENOME_TYPE_ARRAY)


def gem_a2_manifest_workflow():
    """
    Entrypoint for GEM A2 Workflow
    """
    with GenomicJobController(GenomicJob.GEM_A2_MANIFEST,
                              bucket_name=config.GENOMIC_GEM_BUCKET_NAME) as controller:
        controller.run_gem_a2_workflow()


def gem_a3_manifest_workflow():
    """
    Entrypoint for GEM A3 Workflow
    """
    with GenomicJobController(GenomicJob.GEM_A3_MANIFEST,
                              bucket_name=config.GENOMIC_GEM_BUCKET_NAME) as controller:
        controller.generate_manifest(GenomicManifestTypes.GEM_A3, _genome_type=config.GENOME_TYPE_ARRAY)


def create_cvl_reconciliation_report():
    """
    Entrypoint for CVL reconciliation workflow
    Sources from genomic_set_member and produces CVL reconciliation report CSV
    """
    with GenomicJobController(GenomicJob.CVL_RECONCILIATION_REPORT) as controller:
        controller.run_cvl_reconciliation_report()


def create_cvl_manifests():
    """
    Entrypoint for CVL Manifest workflow
    Sources from list of biobank_ids from CVL reconciliation report
    """
    with GenomicJobController(GenomicJob.CREATE_CVL_MANIFESTS) as controller:
        controller.generate_manifest(GenomicManifestTypes.DRC_CVL_WGS, _genome_type=config.GENOME_TYPE_WGS)
