"""
TestReportGeneratorService
"""

from api.service.report_generator_service import report_generator_service
from api.tests.repository import idea_reply_data
from api.utils.remove_pdfs_and_docs import remove_pdf_and_doc


class TestReportGeneratorService:
    """
    TestReportGeneratorService
    """

    def test_a_report_gen_with_empty_data(self):
        """
        Test a report generator with empty data
        """

        docs = report_generator_service.export_docx(data={})
        assert docs

        pdf = report_generator_service.export_pdf(data={})
        assert pdf

        remove_pdf_and_doc(filename=pdf, is_pdf=True)
        remove_pdf_and_doc(filename=docs, is_docx=True)

    def test_b_report_gen_without_validation_output(self):
        """
        Test b report generator without validation output
        """
        data = idea_reply_data
        data.pop("B. Launch Content Generator", None)
        data.pop("C. Influencer Outreach Generator", None)

        docs = report_generator_service.export_docx(data={})
        assert docs

        pdf = report_generator_service.export_pdf(data={})
        assert pdf

        remove_pdf_and_doc(filename=pdf, is_pdf=True)
        remove_pdf_and_doc(filename=docs, is_docx=True)

    def test_c_report_gen_without_launch_content_generator(self):
        """
        Test c report generator without launch content generator
        """
        data = idea_reply_data
        data.pop("A. Validation Output", None)
        data.pop("C. Influencer Outreach Generator", None)

        docs = report_generator_service.export_docx(data={})
        assert docs

        pdf = report_generator_service.export_pdf(data={})
        assert pdf

        remove_pdf_and_doc(filename=pdf, is_pdf=True)
        remove_pdf_and_doc(filename=docs, is_docx=True)

    def test_d_report_gen_without_influencer_outreach(self):
        """
        Test d report generator without influencer outreach
        """
        data = idea_reply_data
        data.pop("A. Validation Output", None)
        data.pop("B. Launch Content Generator", None)

        docs = report_generator_service.export_docx(data={})
        assert docs

        pdf = report_generator_service.export_pdf(data={})
        assert pdf

        remove_pdf_and_doc(filename=pdf, is_pdf=True)
        remove_pdf_and_doc(filename=docs, is_docx=True)
