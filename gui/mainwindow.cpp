#include "mainwindow.h"
#include "sysview.h"
#include "pidview.h"
#include "plotview.h"
#include "data.h"

#include <QtXml>
#include <iostream>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
	data = new Data();

	createView();
    createActions();
    createMenu();

	proc = new QProcess(this);
	proc->setProcessChannelMode(QProcess::MergedChannels);
	connect(proc, SIGNAL(readyReadStandardOutput()), this, SLOT(onReadOutput()));
	connect(proc, SIGNAL(readyReadStandardError()), this, SLOT(onReadError()));
	connect(proc, SIGNAL(finished(int, QProcess::ExitStatus)), this, SLOT(onRunFinished(int, QProcess::ExitStatus)));
	connect(proc, SIGNAL(errorOccurred(QProcess::ProcessError)), this, SLOT(onRunError(QProcess::ProcessError)));

	readSettings();
}

MainWindow::~MainWindow()
{
	writeSettings();
	delete data;
}

void MainWindow::open()
{
	QString filter = "PID File (*.xml)";
	QString filename;
	QFileDialog *fd = new QFileDialog(this, tr("Open..."), QDir::currentPath(), filter);
	fd->setAcceptMode(QFileDialog::AcceptOpen);

	if (fd->exec() == QFileDialog::Accepted)
		filename = fd->selectedFiles().at(0);
	else
		return;

	if (!filename.endsWith(".xml"))
		filename = filename + ".xml";
	
	QFile file(QString::fromLocal8Bit(filename.toLocal8Bit()));
	if (!file.open(QFile::ReadOnly | QFile::Text)) {
		QMessageBox::warning(this, tr("Loading from file"),
			QString(tr("Cannot read file %1:\n%2")).arg(filename).arg(file.errorString()));
		return;
	}

	QDomDocument doc;
	doc.setContent(&file);
	QDomElement rootElement = doc.documentElement();

	data->clear();
	data->loadFromDom(rootElement);

	file.close();
	QDir::setCurrent(QFileInfo(filename).absolutePath());

	updateView();
}

void MainWindow::save()
{
	QString filter = "PID File (*.xml)";
	QString filename;
	QFileDialog *fd = new QFileDialog(this, tr("Save..."), QDir::currentPath(), filter);
	fd->setAcceptMode(QFileDialog::AcceptSave);

	if (fd->exec() == QFileDialog::Accepted)
		filename = fd->selectedFiles().at(0);
	else
		return;

	if (!filename.endsWith(".xml"))
		filename = filename + ".xml";

	QFile file(QString::fromLocal8Bit(filename.toLocal8Bit()));
	if (!file.open(QFile::WriteOnly | QFile::Text)) {
		QMessageBox::warning(this, tr("Loading from file"),
			QString(tr("Cannot read file %1:\n%2")).arg(filename).arg(file.errorString()));
		return;
	}

	QTextStream out(&file);

	QDomDocument doc;
	QDomElement rootElement = doc.createElement("PID");
	doc.appendChild(rootElement);

	data->saveToDom(doc, rootElement);

	doc.save(out, 4);

	file.close();
	QDir::setCurrent(QFileInfo(filename).absolutePath());
}

void MainWindow::run()
{
	QString runPath = QApplication::applicationDirPath() + "/../../temp";
	QString programPath = QApplication::applicationDirPath() + "/../../core";

	QString program = "C:\\Program\ Files\\Anaconda3\\python.exe";
	QStringList arguments;
	arguments << QString("%1/main.py").arg(programPath);

	console->append(program);
	console->append(arguments.first());

	proc->setWorkingDirectory(runPath);
	proc->start(program, arguments);
}

void MainWindow::onReadOutput()
{
	QByteArray ba = proc->readAllStandardOutput();
	console->append(ba);
}

void MainWindow::onReadError()
{
	QByteArray ba = proc->readAllStandardError();
	console->append(ba);
	console->show();
}

void MainWindow::onRunFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
	QString runPath = QApplication::applicationDirPath() + "/../../temp";
	if (exitStatus == QProcess::NormalExit)
	{
		if (exitCode == 0) {

			updateFromFile(runPath + "/output.xml");
			viewer->open(runPath + "/blade.xyz", ModelView::PLOT3D);
			ugnxAct->setEnabled(true);
		}
		else {
			QString text = QString("<b>Error</b><p>Program exit with code = %1</p>").arg(exitCode);
			console->append(text);
			console->show();
			ugnxAct->setEnabled(false);
		}
	}
	else {
		QString msg = QString("Program crashed with code = %1").arg(exitCode);
		QMessageBox::information(this, "Error", msg);
		ugnxAct->setEnabled(false);
	}

}

void MainWindow::onRunError(QProcess::ProcessError error)
{
	QString msg;
	switch (error)
	{
	case QProcess::FailedToStart:
		msg = "Failed to start";
		break;
	case QProcess::Crashed:
		msg = "Crashed";
		break;
	case QProcess::Timedout:
		msg = "Time out";
		break;
	case QProcess::ReadError:
		msg = "Read error";
		break;
	case QProcess::WriteError:
		msg = "Write error";
		break;
	case QProcess::UnknownError:
		msg = "Unknown error";
		break;
	}

	QMessageBox::information(this, "Error", msg);
}


void MainWindow::createView()
{
	plotview = new PlotView(data, this);

	sysview = new SysView(this);
	pidview = new PIDView(this);
	console = new QTextEdit(this);

	tab = new QTabWidget(this);
	tab->addTab(sysview, tr("System"));
	tab->addTab(pidview, tr("PID"));
	tab->addTab(console, tr("Console"));

	QSplitter *splitter = new QSplitter(Qt::Horizontal, this);
	splitter->setHandleWidth(0);
	splitter->addWidget(plotview);
	splitter->addWidget(tab);
	splitter->setStretchFactor(0, 1);
	setCentralWidget(splitter);
}

void MainWindow::createActions()
{
	//	File

    openAct = new QAction(tr("Open"), this);
	openAct->setShortcuts(QKeySequence::Open);
    connect(openAct, SIGNAL(triggered(bool)), this, SLOT(open()));

    saveAct = new QAction(tr("Save"), this);
	saveAct->setShortcuts(QKeySequence::Save);
    connect(saveAct, SIGNAL(triggered(bool)), this, SLOT(save()));

	exitAct = new QAction(tr("Exit"), this);
	exitAct->setShortcuts(QKeySequence::Quit);
	connect(exitAct, SIGNAL(triggered(bool)), qApp, SLOT(exit()));

	//	Analysis

	runAct = new QAction(tr("Run"), this);
	runAct->setShortcut(QKeySequence(Qt::Key_F5));
	connect(runAct, SIGNAL(triggered(bool)), this, SLOT(run()));
}

void MainWindow::createMenu()
{
    QMenu *fileMenu = menuBar()->addMenu(tr("File"));
    fileMenu->addAction(openAct);
    fileMenu->addAction(saveAct);
	fileMenu->addSeparator();
	fileMenu->addAction(exitAct);

	QMenu *analysisMenu = menuBar()->addMenu(tr("Analysis"));
	analysisMenu->addAction(runAct);
}

void MainWindow::readSettings()
{
	QSettings settings("ACTECH", "PIDcontrol");

	QDir::setCurrent(settings.value("current-path").toString());

	//  Window Geometry
	restoreGeometry(settings.value("geometry").toByteArray());
	restoreState(settings.value("state").toByteArray());
	setCorner(Qt::TopLeftCorner, Qt::TopDockWidgetArea);
	setCorner(Qt::TopRightCorner, Qt::TopDockWidgetArea);
	setCorner(Qt::BottomLeftCorner, Qt::LeftDockWidgetArea);
	setCorner(Qt::BottomRightCorner, Qt::RightDockWidgetArea);

	move(settings.value("pos", QPoint(200, 200)).toPoint());
	resize(settings.value("size", QSize(800, 600)).toSize());

	QString winstate = settings.value("window-state", "normal").toString();
	if (winstate == "maximized")
		setWindowState(Qt::WindowMaximized);
	else if (winstate == "fullscreen")
		setWindowState(Qt::WindowFullScreen);
	else
		setWindowState(Qt::WindowNoState);
}

void MainWindow::writeSettings()
{
	QSettings settings("ACTECH", "PIDcontrol");

	//  Window Geometry
	if ((!isMaximized()) && (!isMinimized())) {
		settings.setValue("pos", pos());
		settings.setValue("size", size());
	}
	if (isMaximized())
		settings.setValue("window-state", "maximized");
	else if (isFullScreen())
		settings.setValue("window-state", "fullscreen");
	else
		settings.setValue("window-state", "normal");
	settings.setValue("state", saveState());

	//  File & Path
	settings.setValue("current-path", QDir::currentPath());
}


void MainWindow::updateView()
{
	plotview->replot();
}

bool MainWindow::loadFromFile(QString filename)
{
	QFile file(QString::fromLocal8Bit(filename.toLocal8Bit()));
	if (!file.open(QFile::ReadOnly | QFile::Text)) {
		QMessageBox::warning(this, tr("Loading from file"),
			QString(tr("Cannot read file %1:\n%2")).arg(filename).arg(file.errorString()));
		return false;
	}

	QDomDocument doc;
	doc.setContent(&file);
	QDomElement rootElement = doc.documentElement();

	data->clear();
	data->loadFromDom(rootElement);

	file.close();
	QDir::setCurrent(QFileInfo(filename).absolutePath());

	updateView();

	return true;
}