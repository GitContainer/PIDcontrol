#include "plotview.h"
#include "data.h"

PlotChart::PlotChart()
	: QChart()
{
	grabGesture(Qt::PanGesture);
	grabGesture(Qt::PinchGesture);
}

PlotChart::~PlotChart()
{

}


bool PlotChart::sceneEvent(QEvent *event)
{
	if (event->type() == QEvent::Gesture)
		return gestureEvent(static_cast<QGestureEvent *>(event));
	return QChart::event(event);
}

bool PlotChart::gestureEvent(QGestureEvent *event)
{
	if (QGesture *gesture = event->gesture(Qt::PanGesture)) {
		QPanGesture *pan = static_cast<QPanGesture *>(gesture);
		QChart::scroll(-(pan->delta().x()), pan->delta().y());
	}

	if (QGesture *gesture = event->gesture(Qt::PinchGesture)) {
		QPinchGesture *pinch = static_cast<QPinchGesture *>(gesture);
		if (pinch->changeFlags() & QPinchGesture::ScaleFactorChanged)
			QChart::zoom(pinch->scaleFactor());
	}

	return true;
}

//=================================================================================

PlotChartView::PlotChartView(QChart *chart, QWidget *parent)
	: QChartView(chart, parent)
{
	isTouching = false;
	setRubberBand(QChartView::RectangleRubberBand);
}

bool PlotChartView::viewportEvent(QEvent *event)
{
	if (event->type() == QEvent::TouchBegin)
	{
		isTouching = true;
		chart()->setAnimationOptions(QChart::NoAnimation);
	}

	return QChartView::viewportEvent(event);
}

void PlotChartView::mousePressEvent(QMouseEvent *event)
{
	if (isTouching)
		return;
	QChartView::mousePressEvent(event);
}

void PlotChartView::mouseMoveEvent(QMouseEvent *event)
{
	if (isTouching)
		return;
	QChartView::mouseMoveEvent(event);
}

void PlotChartView::mouseReleaseEvent(QMouseEvent *event)
{
	if (isTouching)
		isTouching = false;

	chart()->setAnimationOptions(QChart::SeriesAnimations);

	QChartView::mouseReleaseEvent(event);
}

void PlotChartView::keyPressEvent(QKeyEvent *event)
{
	switch (event->key()) {
	case Qt::Key_Plus:
		chart()->zoomIn();
		break;
	case Qt::Key_Minus:
		chart()->zoomOut();
		break;
	case Qt::Key_Left:
		chart()->scroll(-10, 0);
		break;
	case Qt::Key_Right:
		chart()->scroll(10, 0);
		break;
	case Qt::Key_Up:
		chart()->scroll(0, 10);
		break;
	case Qt::Key_Down:
		chart()->scroll(0, -10);
		break;
	default:
		QGraphicsView::keyPressEvent(event);
		break;
	}
}

//=================================================================================

PlotView::PlotView(Data *pData, QWidget *parent)
	: QWidget(parent)
{
	_data = pData;

	d_chart = new PlotChart();
	d_chart->setMargins(QMargins(0, 0, 0, 0));

	d_view = new PlotChartView(d_chart, this);
	d_view->setRenderHint(QPainter::Antialiasing);

	QGridLayout *layout = new QGridLayout();
	layout->setMargin(0);
	layout->setSpacing(0);
	layout->addWidget(d_view);
	setLayout(layout);

	grabGesture(Qt::PanGesture);
	grabGesture(Qt::PinchGesture);

	QLineSeries *series = new QLineSeries(this);
	d_chart->addSeries(series);

	d_chart->setBackgroundVisible(false);
	d_chart->setPlotAreaBackgroundVisible(false);
	d_chart->legend()->setAlignment(Qt::AlignRight);
	d_chart->legend()->setContentsMargins(0, 0, 0, 0);
	d_chart->legend()->setVisible(true);

	d_chart->createDefaultAxes();
	QAbstractAxis *axisX = d_chart->axisX();
	QAbstractAxis *axisY = d_chart->axisY();
	axisX->setRange(0,1);
	axisY->setRange(0,1);
}

PlotView::~PlotView()
{
}

void PlotView::replot()
{
	d_chart->removeAllSeries();

	int ndim = _data->dimension();
	int nstep = _data->nstep();
	double ymin = 0;
	double ymax = 0;

	QString colors[] = {
		"#ff0000",
		"#00ff00",
		"#ffff00",
		"#0000ff",
		"#00ffff",
		"#ff00ff",
		"#008b8b",
		"#006400",
		"#800080",
		"#8b0000",
		"#808000",
		"#d3d3d3",
		"#a9a9a9",
		"#000000"
	};

	for (int idim = 0; idim < ndim; idim++)
	{
		QLineSeries *series = new QLineSeries(this);
		series->setName(QString("Dim %1").arg(idim + 1));

		QLineSeries *target = new QLineSeries(this);
		target->setName(QString("Dim %1 (target)").arg(idim + 1));

		for (int istep = 0; istep < nstep; istep++) {
			double t = _data->getTime(istep);
			double x = _data->getValue(istep, idim);
			double r = _data->getTarget(istep, idim);
			series->append(t, x);
			target->append(t, r);

			if (x < ymin)	ymin = x;
			if (r < ymin)	ymin = r;
			if (x > ymax)	ymax = x;
			if (r > ymax)	ymax = r;
		}

		QColor color(colors[idim % 14]);

		QPen pen;
		pen.setColor(color);
		pen.setWidth(1);
		pen.setStyle(Qt::SolidLine);
		series->setPen(pen);

		pen.setStyle(Qt::DashLine);
		target->setPen(pen);

		d_chart->addSeries(series);
		d_chart->addSeries(target);
	}

	d_chart->createDefaultAxes();
	QAbstractAxis *axisX = d_chart->axisX();
	QAbstractAxis *axisY = d_chart->axisY();
	axisX->setRange(_data->getStartingTime(), _data->getEndingTime());
	axisY->setRange(ymin, ymax);
}