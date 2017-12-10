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
	void run();
	void onReadOutput();
	void onReadError();
	void onRunFinished(int exitCode, QProcess::ExitStatus exitStatus);
	void onRunError(QProcess::ProcessError error);

private:
	void createView();
    void createActions();
    void createMenu();

	void readSettings();
	void writeSettings();

	void updateView();

	bool loadFromFile(QString filename);

    QAction *openAct, *saveAct, *exitAct;
	QAction *runAct;

	QTabWidget *tab;
	PlotView *plotview;
	PIDView *pidview;
	SysView *sysview;
	QTextEdit *console;

	Data *data;

	QProcess *proc;
};

#endif // MAINWINDOW_H
