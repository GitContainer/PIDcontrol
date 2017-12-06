#pragma once

#include <QtCharts>

class Data;

class PlotChart : public QChart
{
	Q_OBJECT

public:
	PlotChart();
	~PlotChart();

	bool sceneEvent(QEvent *event);
	bool gestureEvent(QGestureEvent *event);
};

class PlotChartView : public QChartView
{
	Q_OBJECT

public:
	PlotChartView(QChart *chart, QWidget *parent = NULL);

protected:
	bool viewportEvent(QEvent *event);
	void mousePressEvent(QMouseEvent *event);
	void mouseMoveEvent(QMouseEvent *event);
	void mouseReleaseEvent(QMouseEvent *event);
	void keyPressEvent(QKeyEvent *event);

private:
	bool isTouching;
};

class PlotView : public QWidget
{
	Q_OBJECT

public:
	PlotView(Data *pData, QWidget *parent = NULL);
	~PlotView();

	void replot();

private:
	PlotChart *d_chart;
	PlotChartView *d_view;

	Data *_data;
};
