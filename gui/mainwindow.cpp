#include "mainwindow.h"
#include "sysview.h"
#include "pidview.h"
#include "plotview.h"
#include "data.h"

#include <QtXml>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
	data = new Data();

	createView();
    createActions();
    createMenu();
}

MainWindow::~MainWindow()
{
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

void MainWindow::createView()
{
	plotview = new PlotView(data, this);

	sysview = new SysView(this);
	pidview = new PIDView(this);

	tab = new QTabWidget(this);
	tab->addTab(sysview, tr("System"));
	tab->addTab(pidview, tr("PID"));

	QSplitter *splitter = new QSplitter(Qt::Horizontal, this);
	splitter->setHandleWidth(0);
	splitter->addWidget(plotview);
	splitter->addWidget(tab);
	splitter->setStretchFactor(0, 1);
	setCentralWidget(splitter);
}

void MainWindow::createActions()
{
    openAct = new QAction(tr("Open"), this);
	openAct->setShortcuts(QKeySequence::Open);
    connect(openAct, SIGNAL(triggered(bool)), this, SLOT(open()));

    saveAct = new QAction(tr("Save"), this);
	saveAct->setShortcuts(QKeySequence::Save);
    connect(saveAct, SIGNAL(triggered(bool)), this, SLOT(save()));
}

void MainWindow::createMenu()
{
    QMenu *fileMenu = menuBar()->addMenu(tr("File"));
    fileMenu->addAction(openAct);
    fileMenu->addAction(saveAct);
}

void MainWindow::updateView()
{
	plotview->replot();
}