#include <QtGui>
 
class HeaderObject : public QWidget{
public:
HeaderObject(QWidget *parent = 0) : QWidget(parent){
QComboBox *c = new QComboBox(this);
QCheckBox *cb = new QCheckBox(this);
c->addItem("test");
c->addItem("test2");
QGridLayout *l = new QGridLayout;
l->addWidget(c);
l->addWidget(cb);
setLayout(l);
}
};
 
class CustomHeader : public QHeaderView{
public:
CustomHeader(QWidget *parent = 0):QHeaderView(Qt::Horizontal, parent){
 
for(int i = 0; i<5; i++){
headerSections.insert(i,new HeaderObject(this));
headerSections[i]->hide();
}
setFont(QFont("Helvetica [Cronyx]", 32));
setMinimumSectionSize(headerSections[0]->minimumSizeHint().width());
setDefaultSectionSize(headerSections[0]->minimumSizeHint().width());
}
protected:
void paintSection(QPainter *painter, const QRect &rect, int logicalIndex) const {
 
if (!rect.isValid())
return;
qDebug() << logicalIndex;
qDebug() << "QRect: " << rect << " AND OFFSET:" << offset();
headerSections[logicalIndex]->setGeometry(rect);
headerSections[logicalIndex]->show();
}
 
private:
QVector< QPointer <HeaderObject> > headerSections;
};
 
 
class CustomModel : public QAbstractTableModel{
public:
CustomModel() : QAbstractTableModel(){
}
 
int rowCount(const QModelIndex &parent = QModelIndex()) const{return 5;}
int columnCount(const QModelIndex &parent = QModelIndex()) const {return 5;}
QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const{
if (role == Qt::DisplayRole) return QVariant();
return QVariant();
}
};
 
int main(int argc, char *argv[])
{
QApplication a(argc, argv);
 
CustomModel *model = new CustomModel;
QTableView *view = new QTableView();
view->setModel(model);
view->setHorizontalHeader(new CustomHeader(view));
view->show();
return a.exec();
}