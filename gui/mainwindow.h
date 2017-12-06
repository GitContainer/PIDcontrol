#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtWidgets>

class PIDView;
class SysView;
class PlotView;

class Data;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent=NULL);
	~MainWindow();

private slots:
    void open();
    void save();

private:
	void createView();
    void createActions();
    void createMenu();

	void updateView();

    QAction *openAct, *saveAct;

	QTabWidget *tab;
	PlotView *plotview;
	PIDView *pidview;
	SysView *sysview;

	Data *data;
};

#endif // MAINWINDOW_H
