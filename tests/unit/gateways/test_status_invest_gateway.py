from decimal import Decimal, InvalidOperation
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError, ClientSession

from app.domain.fii_domain import FiiDomain
from app.gateways.status_invest_gateway import FiiGateway, StatusInvestGateway


class TestStatusInvestGateway:
    @pytest.fixture
    def mock_session(self):
        return MagicMock(spec=ClientSession)

    @pytest.fixture
    def gateway(self, mock_session):
        return StatusInvestGateway(session=mock_session)

    @pytest.fixture
    def gateway_without_session(self):
        return StatusInvestGateway()

    @pytest.mark.asyncio
    async def test_list_returns_ticker_list(self, gateway, mock_session):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value=[{"url": "https://example.com/fii/TEST11"}, {"url": "https://example.com/fii/TEST12"}]
        )
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await gateway.list()

        assert result == ["TEST11", "TEST12"]
        mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_with_empty_response(self, gateway, mock_session):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[])
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await gateway.list()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_returns_fii_domain(self, gateway, mock_session):
        html_content = self._build_valid_html()
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=html_content)
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("app.gateways.status_invest_gateway.etree.HTMLParser"):
            with patch("app.gateways.status_invest_gateway.etree.HTML") as mock_html:
                mock_tree = MagicMock()
                mock_tree.xpath.return_value = ["10.0"]
                mock_html.return_value = mock_tree

                with patch("app.gateways.status_invest_gateway.DataCrawlerConverter") as mock_converter:
                    mock_converter.to_date_or_none.return_value = None
                    mock_converter.to_decimal.return_value = Decimal("10.0")
                    mock_converter.to_decimal_or_none.return_value = Decimal("5.0")

                    result = await gateway.get("TEST11")

        assert isinstance(result, FiiDomain)
        assert result.ticker == "TEST11"

    @pytest.mark.asyncio
    async def test_get_handles_client_error(self, gateway, mock_session):
        mock_session.get.side_effect = ClientError("Connection error")

        result = await gateway.get("TEST11")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_invalid_operation(self, gateway, mock_session):
        html_content = self._build_valid_html()
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=html_content)
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch("app.gateways.status_invest_gateway.DataCrawlerConverter") as mock_converter:
            mock_converter.to_decimal.side_effect = InvalidOperation("Invalid decimal")

            result = await gateway.get("TEST11")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_general_exception(self, gateway, mock_session):
        mock_session.get.side_effect = Exception("Connection error")

        result = await gateway.get("TEST11")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_missing_elements(self, gateway, mock_session):
        html_content = "<html><body></body></html>"
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=html_content)
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await gateway.get("TEST11")

        assert result is None

    @pytest.mark.asyncio
    async def test_close_calls_session_close(self, gateway, mock_session):
        mock_session.close = AsyncMock()

        await gateway.close()

        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_html_returns_content(self, gateway, mock_session):
        expected_html = "<html><body>Test</body></html>"
        mock_response = MagicMock()
        mock_response.text = AsyncMock(return_value=expected_html)
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await gateway._fetch_html("http://test.com")

        assert result == expected_html

    def test_gateway_initialization_with_session(self, mock_session):
        gateway = StatusInvestGateway(session=mock_session)

        assert gateway.session == mock_session

    def test_gateway_initialization_without_session(self):
        with patch("app.gateways.status_invest_gateway.ClientSession") as mock_client_session:
            mock_session = MagicMock()
            mock_client_session.return_value = mock_session
            gateway = StatusInvestGateway()

        assert gateway.session == mock_session

    def test_gateway_constants(self, gateway):
        assert gateway.STATUS_INVEST_URL == "https://statusinvest.com.br/fundos-imobiliarios/"
        assert gateway.XPATH_P_VP is not None
        assert gateway.XPATH_SEGMENT is not None

    def _build_valid_html(self):
        return """
        <html>
            <body>
                <main>
                    <div></div>
                    <div>
                        <div>
                            <div>
                                <div>
                                    <div>
                                        <div>
                                            <div>
                                                <div>
                                                    <div>
                                                        <strong>10.5</strong>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <div>
                            <div>
                                <div>
                                    <div>
                                        <div>
                                            <div>
                                                <strong>híbrido</strong>
                                            </div>
                                        </div>
                                        <div></div>
                                        <div>
                                            <div>
                                                <strong>01/01/2020</strong>
                                            </div>
                                        </div>
                                        <div>
                                            <div>
                                                <div>
                                                    <strong>indeterminado</strong>
                                                </div>
                                            </div>
                                        </div>
                                        <div></div>
                                        <div>
                                            <div>
                                                <div>
                                                    <strong>100</strong>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </body>
        </html>
        """


class TestFiiGateway:
    def test_fii_gateway_is_abstract(self):
        gateway = FiiGateway()

        assert hasattr(gateway, "list")
        assert hasattr(gateway, "get")
