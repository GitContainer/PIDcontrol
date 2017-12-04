#include "mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    createActions();
    createMenu();
}

void MainWindow::open()
{

}

void MainWindow::save()
{

}

void MainWindow::createActions()
{
    openAct = new QAction(tr("Open"), this);
    connect(openAct, SIGNAL(triggered(bool)), this, SLOT(open()));

    saveAct = new QAction(tr("Save"), this);
    connect(saveAct, SIGNAL(triggered(bool)), this, SLOT(save()));
}

void MainWindow::createMenu()
{
    QMenu *fileMenu = menuBar()->addMenu(tr("File"));
    fileMenu->addAction(openAct);
    fileMenu->addAction(saveAct);
}
